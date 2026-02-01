---
name: feishu-leave-request
description: Submit a leave request through Feishu (Lark). Use when the user wants to request time off, submit a leave application, or mentions taking leave.
argument-hint: [date] [duration] [type] [reason]
---

# Feishu Leave Request Assistant

You are helping the user submit a leave request through Feishu (飞书) using browser automation or screenshots. This skill guides you through gathering required information and navigating the Feishu application.

## Step 1: Gather Required Information

Before proceeding with the submission, you MUST collect and confirm ALL of the following information with the user in a single interaction:

### 1. Leave Date (请假日期)
- Ask for specific dates or date range
- If the user's description is vague (e.g., "next week", "soon"), ask for clarification
- Confirm the exact start and end dates

### 2. Leave Duration (请假时长)
- Half day (半天)
- Full day (一天)
- Multiple days (几天)

### 3. Leave Type (请假类型)
Choose from:
- Annual leave (年假)
- Personal leave (事假)
- Sick leave (病假)
- Parental leave (育儿假)
- Maternity leave (产假)
- Paternity leave (陪产假)

### 4. Leave Reason (请假原因)
- Brief explanation for the leave request
- Should be clear and professional

## Step 2: Confirm All Information

Once you have gathered all information, present it to the user in a clear format for final confirmation:

```
Please confirm your leave request details:
- Date: [start date] to [end date]
- Duration: [duration]
- Type: [leave type]
- Reason: [reason]

Is this information correct? (Yes/No)
```

## Step 3: Navigate Feishu Application

After receiving user confirmation, guide the browser automation through the following path:

### Primary Navigation Path:
1. **Open Feishu** (only desktop app)
2. **Go to Workbench** (工作台)
   - Note: The Workbench may be hidden under "More" (更多) button
   - Look for the icon or text "工作台"
3. **Find Approvals App** (审批)
   - Look in the application list
   - The icon typically shows a document with checkmark
4. **Click "Initiate Request"** (发起申请)
5. **Select "Leave Request"** (请假)
6. **Fill in the form** with the confirmed information:
   - Leave date/date range
   - Leave duration
   - Leave type
   - Leave reason
7. **Submit the request**

### Alternative Path (if Approvals app is not visible):
1. Use Feishu's **search function** (搜索)
2. Search for "审批" (Approvals)
3. Open the Approvals app from search results
4. Continue from step 4 in the primary path

## Step 4: Verification

After submission, verify with the user:
- Was the request successfully submitted?
- Did they receive a confirmation message or notification?
- Is there a request ID or reference number?

## Important Notes

- **Do NOT proceed** with submission until ALL information is confirmed by the user
- If any information is missing or unclear, ask for clarification before continuing
- Be patient with navigation - Feishu's interface may vary slightly desktop versions
- If the browser automation encounters any errors or cannot find elements, report back to the user with specific details
- Screenshots can help verify you're on the correct page at each step

## Error Handling

If you encounter issues:
- **Cannot find Workbench**: Check under "More" (更多) or use search
- **Cannot find Approvals app**: Use the search function to find "审批"
- **Form fields don't match**: Ask the user to provide a screenshot of the current page
- **Submission fails**: Check for validation errors and report them to the user
