# Recreation.gov Availability API Notes

## Endpoints

### Availability (Monthly)
```
GET https://www.recreation.gov/api/camps/availability/campground/{id}/month
?start_date=YYYY-MM-01T00:00:00.000Z
```

Returns all campsites with availability status for the month.

### Campground Info
```
GET https://www.recreation.gov/api/camps/campgrounds/{id}
```

Returns campground metadata, description, activities, addresses.

### Campsite Details
```
GET https://www.recreation.gov/api/camps/campsites/{id}
```

Returns detailed site info including amenities, equipment, attributes.

## Availability Status Values

| Status | Meaning |
|--------|---------|
| `Available` | Can be booked |
| `Reserved` | Already booked |
| `Not Available` | Closed/unavailable |
| `NYR` | Not Yet Released (future date) |
| `Open` | Open but not reservable |

## Campsite Type Values

Common types from `campsite_type` field:

- `TENT ONLY NONELECTRIC`
- `TENT ONLY ELECTRIC`
- `STANDARD NONELECTRIC`
- `STANDARD ELECTRIC`
- `RV NONELECTRIC`
- `RV ELECTRIC`
- `CABIN NONELECTRIC`
- `CABIN ELECTRIC`
- `GROUP STANDARD NONELECTRIC`
- `GROUP STANDARD ELECTRIC`
- `EQUESTRIAN NONELECTRIC`
- `MANAGEMENT`
- `LOOKOUT`
- `YURT`

## Site Attributes (from campsite details)

### site_details_map
- `campfire_allowed`: Yes/No
- `capacity_rating`: Single/Double/Triple/Group
- `pets_allowed`: Yes/No
- `shade`: Full/Partial/No
- `checkin_time`, `checkout_time`
- `max_num_people`, `min_num_people`

### equipment_details_map
- `driveway_entry`: Back-In/Pull-Through
- `driveway_surface`: Paved/Gravel/Native
- `driveway_grade`: Level/Moderate/Steep
- `max_num_vehicles`
- `max_vehicle_length`

### amenities (array)
- `fire_pit`: Y/N
- `picnic_table`: Y/N
- `bbq`: Y/N
- `water_hookup`: Y/N
- `electric_hookup`: Y/N (30/50 amp info may be in value)
- `sewer_hookup`: Y/N

## Rate Limits

No documented rate limits, but:
- Add reasonable delays between bulk requests
- Use a proper User-Agent header
- The API is public but unofficial

## References

- Recreation.gov: https://www.recreation.gov
- RIDB Portal: https://ridb.recreation.gov
