class Queries:

    q1_campaignnnn_daily_all_channel_type_overall = """
        SELECT
            segments.date,
            campaign.name,
            campaign.advertising_channel_type,
            campaign.status,
            campaign.optimization_score,
            campaign.bidding_strategy_type,
            metrics.impressions,
            metrics.clicks,
            metrics.average_cpc,
            metrics.cost_micros,
            metrics.search_impression_share,
            metrics.active_view_cpm,
            metrics.average_cpv,
            metrics.video_views,
            metrics.video_view_rate           
        FROM campaign 
        WHERE 
            segments.date BETWEEN '2024-01-01' AND '2024-12-31' 
            AND campaign.status IN ('ENABLED', 'PAUSED', 'REMOVED')
            AND campaign.advertising_channel_type IN ('DISCOVERY', 'DISPLAY', 'PERFORMANCE_MAX', 'SEARCH', 'SHOPPING', 'VIDEO')
            AND campaign.bidding_strategy_type IN ('COMMISSION', 'ENHANCED_CPC', 'INVALID', 'MANUAL_CPA', 'MANUAL_CPC', 'MANUAL_CPM', 'MANUAL_CPV', 'MAXIMIZE_CONVERSIONS', 'MAXIMIZE_CONVERSION_VALUE', 'PAGE_ONE_PROMOTED', 'PERCENT_CPC', 'TARGET_CPA', 'TARGET_CPM', 'TARGET_IMPRESSION_SHARE', 'TARGET_OUTRANK_SHARE', 'TARGET_ROAS', 'TARGET_SPEND', 'UNKNOWN')
    """

    q2_conversion_category='''
SELECT campaign.name,metrics.all_conversions,metrics.conversions,metrics.conversions_value,campaign_budget.amount_micros, segments.conversion_action_category, segments.date FROM campaign WHERE segments.conversion_action_category IN ('ADD_TO_CART', 'BEGIN_CHECKOUT', 'BOOK_APPOINTMENT', 'CONTACT', 'CONVERTED_LEAD', 'DEFAULT', 'DOWNLOAD', 'ENGAGEMENT', 'GET_DIRECTIONS', 'IMPORTED_LEAD', 'OUTBOUND_CLICK', 'PAGE_VIEW', 'PHONE_CALL_LEAD', 'PURCHASE', 'QUALIFIED_LEAD', 'REQUEST_QUOTE', 'SIGNUP', 'STORE_SALE', 'STORE_VISIT', 'SUBMIT_LEAD_FORM', 'SUBSCRIBE_PAID', 'UNKNOWN') AND segments.date BETWEEN '2023-01-01' AND '2023-12-31'
    '''

    q3_bidding_strategy='''
    SELECT bidding_strategy.campaign_count, bidding_strategy.status, bidding_strategy.name, bidding_strategy.type, metrics.clicks, metrics.impressions, metrics.cost_micros, metrics.conversions_value, metrics.conversions FROM bidding_strategy WHERE segments.date DURING LAST_30_DAYS
    '''

    q4_local = '''
SELECT campaign_criterion.location.geo_target_constant,
  campaign.name,
  campaign_criterion.bid_modifier,
  metrics.clicks,
  metrics.impressions,
  metrics.ctr,
  metrics.average_cpc,
  metrics.cost_micros
FROM location_view
WHERE segments.date DURING LAST_7_DAYS
  AND campaign_criterion.status != 'REMOVED'
    '''
    q5_video='''
SELECT segments.date, campaign.name,campaign.advertising_channel_type, campaign.status, metrics.video_views,metrics.video_view_rate,metrics.cost_micros, metrics.video_quartile_p25_rate, metrics.video_quartile_p50_rate, metrics.video_quartile_p75_rate, metrics.video_quartile_p100_rate,metrics.average_cpv FROM campaign WHERE segments.date DURING YESTERDAY AND campaign.advertising_channel_type IN ('DISPLAY', 'PERFORMANCE_MAX', 'VIDEO') 

    '''

    q2_gads_campaign_daily_overall = """
        SELECT
            metrics.impressions,
            metrics.clicks,
            metrics.average_cpc,
            metrics.cost_micros,
            metrics.conversions_value,
            metrics.conversions,
            metrics.search_impression_share,
            metrics.active_view_cpm,
            segments.date
        FROM campaign 
        WHERE 
            segments.date DURING YESTERDAY 
            AND campaign.status IN ('ENABLED') 
    """


