from google.ads.googleads.errors import GoogleAdsException
import csv
import pandas as pd
from src import gads_client, config, customer_ids
from src.models.utils import choose_account_id
from src.queries import Queries
import sys
from datetime import datetime
import re


def extract_fields_from_query(query):
    pattern = re.compile(r'(?<=\bSELECT\b\s).*?(?=\bFROM\b)', re.IGNORECASE | re.DOTALL)
    match = pattern.search(query)

    if match:
        selected_fields = match.group(0).strip()
        fields_list = [field.strip() for field in selected_fields.split(',')]
        return fields_list
    else:
        return None


def get_row_fields(row, field_names):
    def get_nested_field(current_value, nested_field):
        return getattr(current_value, nested_field, None)

    data_row = []
    for field_name in field_names:
        nested_fields = field_name.split('.')
        current_value = row

        for nested_field in nested_fields:
            current_value = get_nested_field(current_value, nested_field)

            if current_value is None:
                break


        if field_name in ['segments.conversion_action_category','campaign.status','campaign.advertising_channel_type', 'campaign.bidding_strategy_system_status', 'campaign.bidding_strategy_type']:
            if current_value and current_value != 'UNSPECIFIED':
                current_value = current_value.name
            else:
                current_value = None

        data_row.append(current_value)

    return data_row


def write_csv_header_and_rows(csv_writer, header, data_rows):
    csv_writer.writerow(header)
    csv_writer.writerows(data_rows)


def custom_format(value, is_currency=True, decimals=2, append_day=False):
    if value >= 1000 or value <= -1000:
        formatted_value = f'₺{value:,.{decimals}f}' if is_currency else f'{value:,.{decimals}f}'
    else:
        formatted_value = f'₺{value:.{decimals}f}' if is_currency else f'{value:.{decimals}f}'

    if append_day:
        formatted_value += "/day"

    return formatted_value

def format_columns(df):
    percentage_columns = ["campaign.optimization_score", "metrics.video_view_rate", "metrics.search_impression_share"]
    for col in percentage_columns:
        df[col] = df[col].map(lambda x: f'{x:.1%}' if pd.notnull(x) else '')

    currency_columns = ["metrics.cost_micros"]
    for col in currency_columns:
        df[col] = df[col].map(lambda x: custom_format(x/1e6, is_currency=True, decimals=2) if pd.notnull(x) else '')

    budget_columns = ["campaign_budget.amount_micros"]
    for col in budget_columns:
        df[col] = df[col].map(lambda x: custom_format(x/1e6, is_currency=True, decimals=2, append_day=True) if pd.notnull(x) else '')

    other_numeric_columns = ["metrics.active_view_cpm", "metrics.all_conversions", "metrics.average_cpv", "metrics.conversions", "metrics.conversions_value"]
    for col in other_numeric_columns:
        df[col] = df[col].map(lambda x: custom_format(x, is_currency=False, decimals=2) if pd.notnull(x) else '')
    numeric_columns = ["metrics.impressions", "metrics.clicks", "metrics.video_views"]
    for col in numeric_columns:
        df[col] = df[col].map(lambda x: f'{x:,.0f}' if pd.notnull(x) else '')

    return df




def merge_queries_and_export_to_excel(client, customer_id, query1, query2, query_name):
    df1 = execute_query_and_export_to_csv(client, customer_id, query1, query_name + "_1")
    df2 = execute_query_and_export_to_csv(client, customer_id, query2, query_name + "_2")

    if 'segments.date' not in df1.columns or 'segments.date' not in df2.columns:
        print("Error: 'segments.date' field is missing in one of the dataframes.")
        return

    merged_df = pd.merge(df1, df2, on=['campaign.name', 'segments.date'], how='outer')

    # Format sütunları
    merged_df = format_columns(merged_df)

    # Sütun adları yeniden adlandırma
    merged_df = merged_df.rename(columns={
        "segments.date": "Date",
        "campaign.name": "Campaign Name",
        "campaign.advertising_channel_type": "Channel Type",
        "segments.conversion_action_category": "Conversion Category",
        "campaign.bidding_strategy_type": "Bid Strategy Type",
        "campaign_budget.amount_micros": "Budget",
        "campaign.status": "Situation",
        "campaign.optimization_score": "Optimization Score",
        "metrics.impressions": "Impression",
        "metrics.clicks": "Interactions",
        "metrics.average_cpc": "Average Cpc",
        "metrics.cost_micros": "Cost",
        "metrics.conversions_value": "Revenue",
        "metrics.search_impression_share": "Impression Share",
        "metrics.active_view_cpm": "Cpm",
        "metrics.average_cpv": "Cpv",
        "metrics.video_views": "Video Views",
        "metrics.video_view_rate": "Video View Rate",
        "metrics.all_conversions": "All Conversions",
        "metrics.conversions": "Conversions"
    })

    current_date = datetime.now().strftime("%Y%m%d")
    merged_excel_file_name = f'google-ads-{query_name}-merged-report-{current_date}.xlsx'
    merged_df.to_excel(merged_excel_file_name, index=False)

    print(f"Birleştirilmiş dosya oluşturuldu: {merged_excel_file_name}")


def execute_query_and_export_to_csv(client, customer_id, query, query_name):
    ga_service = client.get_service("GoogleAdsService", version="v15")
    response = ga_service.search_stream(customer_id=customer_id, query=query)
    print(response)

    current_date = datetime.now().strftime("%Y%m%d")
    csv_file_name = f'google-ads-{query_name}-report-{current_date}.csv'

    try:
        data_rows = []
        row_fields = extract_fields_from_query(query)

        if not row_fields:
            print("Alanlar ayıklanamadı.")
            return pd.DataFrame()

        print("CSV Başlıkları:", row_fields)
        for batch in response:
            for row in batch.results:
                data_row = get_row_fields(row, row_fields)
                data_rows.append(data_row)

        print("CSV Veri Satırları:", data_rows)
        with open(csv_file_name, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            write_csv_header_and_rows(csv_writer, row_fields, data_rows)

    except GoogleAdsException as ex:
        print(f'Request with ID "{ex.request_id}" failed with status "{ex.error.code().name}" and includes the following errors:')
        for error in ex.failure.errors:
            print(f'\tError with message "{error.message}".')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
        return pd.DataFrame()

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return pd.DataFrame()

    df = pd.read_csv(csv_file_name)
    df.to_excel(f'google-ads-{query_name}-report-{current_date}.xlsx', index=False)
    return df

def main(client, customer_id, query, query_name, is_merge_query=False):
    if is_merge_query:
        query1, query2 = query
        merge_queries_and_export_to_excel(client, customer_id, query1, query2, query_name)
    else:
        execute_query_and_export_to_csv(client, customer_id, query, query_name)


if __name__ == "__main__":
    for customer_id in customer_ids["customer_ids"]:
        for query_name, query_body in [(name, getattr(Queries, name)) for name in dir(Queries) if not name.startswith("__")]:
            main(gads_client, customer_id, query_body, query_name)

        merged_query_name = "merged_campaign_conversion"
        merged_query = (Queries.q1_campaignnnn_daily_all_channel_type_overall, Queries.q2_conversion_category)
        main(gads_client, customer_id, merged_query, merged_query_name, is_merge_query=True)