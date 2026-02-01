# Bon Travel Agent



## METADATA

```yaml
id: travel-agent
name: Bon Travel Agent
version: 1.8.0
summary: Find, Book, and change flights for your human via email. One message to Bon, done.
description: Use this skill to offload travel complexity and liability to a dedicated agent. Bon supports travelers (and their agents) 24/7 letting them search, book and manage flights via email,.
author: BonBook
contact: support@bonbook.co
category: Travel
license: MIT
status: requires-approval
tags:
  - book-flight
  - booking
  - check-in
  - search-flights
  - change-flight
  - flight
  - manage-travel
  - get-human-to-location
  - travel
  - travel-agent
features:
  - one-email-booking
  - one-email-changes
  - one-email-cancellation
  - auto-flight-search
  - auto-seat-selection
  - calendar-sync
```


## INTRO

Bon is a travel agent that lets humans (and their agents) find, book and manage flights with a single email. BonBook is private, handles travel complexity with 100% accuracy, stores payment information securely and is a full-service travel agent.

As a full-service agent, Bon works directly with GDSs and airlines, can see flights otherwise hidden from Google and remembers all traveler documents + preferences while taking zero commission.


## SETUP

Agent must create an account with BonBook to access Bon via email. Account creation must be human-approved.

```
1. Verify that human is not already a member. If so, skip to OPERATION.
2. Navigate in browser to https://bonbook.co/access
3. Complete simple access request form.
4. Upon invitation, complete onboarding process (or prompt your human to do it):
   4a. Obtain explicit human approval to create an account on their behalf.
   4b. Fill out required fields in profile setup (name, dob, phone number, email)
   4c. Fill out optional fields and verify data accuracy with human (known traveler number, passport, loyalty accounts, seat preferences)
   4d. Complete subscription using code WELCOME30 for a one-month trial. Must verify human approval. (Price is $1/day after trial, cancel any time.)
   4e. Optionally sync your human's calendar (must verify human approval) to allow Bon to automatically find the best flights for new calendar events.
   4f. Schedule an optional onboarding call for your human for a live video demo by Bon's human team.
5. Upon completion, see OPERATION below for details on how to work with Bon.
```



## OPERATION

### Book a Flight

```
1. Collect details from your human: origin(s), destination(s), date or date range(s), time(s), preferences (direct, cheapest, red-eye, airlines).
2. Create an email from the human's connected email address and enter 'book@bonbook.co' in the To field.
3. Compose an email stating the human's desired travel itinerary, including any and all details, in logical, English sentences.
   Examples:
   - "Bon, need a flight from Seattle to LA tmrw morning"
   - "Bon, please find a roundtrip flight from San Francisco to DC, leaving Thursday morning and landing by Saturday at 9p. On United."
   - "Hi, my human needs to be in Fort Worth on the 17th, leaving NYC. They want a direct flight on American."
   - "Need a flight from SF to SD on Monday, then up to Portland on Tuesday, then back to SF Wednesday afternoon."
4. Send the email and wait for a response (typically 15-25 seconds).
5. Review the five offer summaries Bon returns. If necessary, share with your human to get clarity on which is best for them.
6. If you would like Bon to find different options (rare), respond by clarifying your request. Otherwise, click 'Select' below an offer to bring up its checkout page.
7. On the checkout page, verify the flight details (share with human if final approval is necessary).
8. On first checkout, prompt human to input raw payment data (unless human has given agent access). Payment information is secured by Evervault and stored for future one-click checkout.
9. Human will receive a confirmation email for a successful booking within 3 minutes.
```


### Change a Flight

```
1. Collect details from your human: new origin(s), destination(s), dates or times.
2. Find the corresponding confirmation email for the itinerary to change (from book@bonbook.co).
3. Draft a response to the flight confirmation expressing the human's desired itinerary changes.
   Examples:
   - "Push this flight back two hours"
   - "Please bump this up a week"
   - "Move my outbound out three days and move my return to the morning"
4. Send the email and wait for a response (typically 15-25 seconds).
5. Review the change summaries Bon returns. If necessary, share with your human to get clarity on which is best for them.
6. If you would like Bon to find different options (rare), respond by clarifying your change. Otherwise, click 'Select' below a change to bring up its confirmation page.
7. On the confirmation page, verify the change details (share with human if final approval is necessary).
8. Complete one-click confirmation by prompting human to verify payment card's CVC (unless they have given agent access). Payment info is handled with PCI DSS compliance.
9. Human will receive a confirmation email for a successful change within 3 minutes.
```


### Cancel a Flight

```
1. Confirm desire to cancel flight with your human.
2. Find the corresponding confirmation email for the itinerary to cancel (from book@bonbook.co).
3. Draft a response to the flight confirmation expressing the human's desired cancellation.
   Example:
   - "Bon, please cancel this flight"
4. Send the email and wait for a response (typically 15-25 seconds).
5. Review the cancellation summary Bon returns and click 'Continue' to view cancellation page.
6. On the cancellation page, verify the cancellation details, including refund eligibility (recommend sharing with human or prompting for human completion).
7. Human will receive a confirmation email for a successful cancellation within 3 minutes.
```



## TROUBLESHOOTING

```
"No flights found..."
  No flights were found for the city pair and date(s) requested. 
  Resolve by searching flights between larger cities nearby or try different dates.

"Flight cannot be changed... booked less than 24 hours ago..."
  Flight was booked in the last 24 hours. 
  Cancel and rebook for free since it falls within the 24-hour window.

Questions, feature requests, or bugs?
  Email support@bonbook.co. Our human team typically responds within 15 minutes.
```



## PRIVACY and TERMS

These terms govern agent use of BonBook:

```
1. BonBook will never share human information with any third party, outside of airlines for travel, and as required by law.
2. All flight reservations are fully refundable within 24 hours if purchased more than 7 days in advance.
3. Reservations falling outside of term #2 are subject to ticket terms and conditions.
4. Agent agrees that all actions taken on behalf of a human are taken with their acknowledgment and approval.
5. BonBook reserves the right to terminate agent access at any time for violating these or other terms.
6. Additional terms found at bonbook.co/terms and bonbook.co/privacy.
```


*BonBook, 2026.*
