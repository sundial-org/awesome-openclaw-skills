# Mayar Integration Examples

Real-world integration patterns for common use cases.

## WhatsApp E-Commerce Bot

### Complete Order Flow

```javascript
// 1. Customer sends order via WhatsApp
// "Mau order wedding template + maintenance 2 bulan"

// 2. Parse order and create invoice
const items = [
  { quantity: 1, rate: 750000, description: "Wedding Website Template" },
  { quantity: 2, rate: 1000000, description: "Monthly Maintenance" }
];

const total = items.reduce((sum, item) => sum + (item.quantity * item.rate), 0);
// Total: 2,750,000

// 3. Create invoice via mcporter
const invoice = execSync(`
  mcporter call mayar.create_invoice \\
    name="Customer Name" \\
    email="customer@email.com" \\
    mobile="\\"6281234567890\\"" \\
    description="Wedding Template + Maintenance Package" \\
    redirectURL="https://yoursite.com/success" \\
    expiredAt="2026-02-07T23:59:59+07:00" \\
    items='${JSON.stringify(items)}' \\
    --output json
`);

const result = JSON.parse(invoice);
const paymentLink = result.data.link.replace('tsrlabs', 'yoursubdomain');

// 4. Format WhatsApp message
const message = `
✅ *Order Confirmed!*

*Package:* Wedding Template + Maintenance

*Items:*
• Wedding Website Template
  Rp 750.000
• Monthly Maintenance x2
  Rp 2.000.000

*TOTAL: Rp 2.750.000*

💳 *Pembayaran:*
${paymentLink}

⏰ Berlaku sampai: 7 Feb 2026

Terima kasih! 🙏
`.trim();

// 5. Send via WhatsApp
message({
  action: 'send',
  channel: 'whatsapp',
  target: '+6281234567890',
  message: message
});
```

### Payment Status Polling

```javascript
// Poll every 30 seconds to check payment status
setInterval(async () => {
  const transactions = execSync(`
    mcporter call mayar.get_latest_transactions page:1 pageSize:10 --output json
  `);
  
  const data = JSON.parse(transactions);
  
  // Check if our invoice ID exists in paid transactions
  const paid = data.data.find(t => 
    t.paymentLinkId === invoiceId && t.status === 'paid'
  );
  
  if (paid) {
    // Send confirmation
    message({
      action: 'send',
      channel: 'whatsapp',
      target: customerPhone,
      message: `
✅ *Pembayaran Berhasil!*

Invoice: #${paid.invoiceCode}
Amount: Rp ${paid.amount.toLocaleString('id-ID')}
Tanggal: ${paid.createdAt}

Setup akan segera dimulai. Terima kasih! 🎉
      `.trim()
    });
    
    clearInterval(this); // Stop polling
  }
}, 30000); // Every 30 seconds
```

## Service Marketplace

### Multi-Service Package

```bash
# Customer orders multiple services
mcporter call mayar.create_invoice \
  name="Business Client" \
  email="client@company.com" \
  mobile="\"6281234567890\"" \
  description="Digital Services Package" \
  redirectURL="https://yoursite.com/success" \
  expiredAt="2026-02-28T23:59:59+07:00" \
  items='[
    {"quantity":1,"rate":5000000,"description":"WhatsApp Bot Setup + CRM"},
    {"quantity":1,"rate":3000000,"description":"Website Development"},
    {"quantity":3,"rate":1000000,"description":"Monthly Maintenance"}
  ]'
```

Total: Rp 11,000,000 (5M + 3M + 3M)

### Recurring Billing Reminder

```javascript
// Check unpaid invoices and send reminders
const unpaid = execSync(`
  mcporter call mayar.get_latest_unpaid_transactions page:1 pageSize:50 --output json
`);

const overdue = JSON.parse(unpaid).data.filter(t => {
  const expiry = new Date(t.paymentLink.expiredAt);
  const soon = Date.now() + (24 * 60 * 60 * 1000); // 24 hours
  return expiry.getTime() < soon && expiry.getTime() > Date.now();
});

// Send reminder for each overdue invoice
overdue.forEach(invoice => {
  message({
    action: 'send',
    channel: 'whatsapp',
    target: invoice.customer.mobile,
    message: `
⏰ *Reminder: Pembayaran akan segera kadaluarsa*

Invoice: #${invoice.invoiceCode}
Amount: Rp ${invoice.amount.toLocaleString('id-ID')}
Kadaluarsa: ${new Date(invoice.paymentLink.expiredAt).toLocaleString('id-ID')}

Link pembayaran:
${invoice.paymentLink.link}

Terima kasih! 🙏
    `.trim()
  });
});
```

## Membership Site

### Check Active Members

```bash
mcporter call mayar.get_membership_customer_by_specific_product \
  productName:"Premium Membership" \
  productLink:"premium-membership" \
  productId:"your-product-uuid" \
  page:1 pageSize:100 \
  memberStatus:"active"
```

### Membership Renewal Automation

```javascript
// Get members expiring soon
const members = execSync(`
  mcporter call mayar.get_membership_customer_by_specific_product \
    productName:"Premium Membership" \
    productLink:"premium-membership" \
    productId:"uuid" \
    page:1 pageSize:100 \
    memberStatus:"active" \
    --output json
`);

const expiringSoon = JSON.parse(members).data.filter(member => {
  const expiry = new Date(member.expirationDate);
  const week = Date.now() + (7 * 24 * 60 * 60 * 1000);
  return expiry.getTime() < week;
});

// Create renewal invoice for each
expiringSoon.forEach(member => {
  const renewalInvoice = createInvoice({
    name: member.customerName,
    email: member.customerEmail,
    mobile: member.customerMobile,
    description: "Premium Membership Renewal",
    items: [
      { quantity: 1, rate: 500000, description: "Premium Membership - 1 Month" }
    ]
  });
  
  // Send renewal notification via email/WhatsApp
});
```

## Course/Digital Product Sales

### Course Purchase with Auto-Access

```javascript
// 1. Create invoice for course
const invoice = createInvoice({
  name: "Student Name",
  email: "student@email.com",
  mobile: "6281234567890",
  description: "Full Stack Development Course",
  items: [
    { quantity: 1, rate: 2500000, description: "Full Stack Dev Course" }
  ]
});

// 2. Monitor payment
pollPayment(invoice.data.id, async (paidInvoice) => {
  // 3. Grant course access
  await grantCourseAccess(paidInvoice.customer.email);
  
  // 4. Send access credentials
  message({
    action: 'send',
    channel: 'whatsapp',
    target: paidInvoice.customer.mobile,
    message: `
🎉 *Pembayaran Berhasil!*

Kamu sekarang memiliki akses ke:
📚 Full Stack Development Course

Login di: https://course.site/login
Email: ${paidInvoice.customer.email}
Password: (cek email)

Selamat belajar! 🚀
    `.trim()
  });
});
```

## Donation Platform

### One-Time Donation

```bash
mcporter call mayar.create_invoice \
  name="Donor Name" \
  email="donor@email.com" \
  mobile="\"6281234567890\"" \
  description="Donation for Education Program" \
  redirectURL="https://donation-site.com/thanks" \
  expiredAt="2026-12-31T23:59:59+07:00" \
  items='[{"quantity":1,"rate":100000,"description":"Education Fund Donation"}]'
```

### Donation with Custom Amount

```javascript
function createDonationInvoice(donorInfo, amount, program) {
  return createInvoice({
    name: donorInfo.name,
    email: donorInfo.email,
    mobile: donorInfo.phone,
    description: `Donation for ${program}`,
    items: [
      { quantity: 1, rate: amount, description: `${program} - Donation` }
    ]
  });
}

// Usage
const donation = createDonationInvoice(
  { name: "John Doe", email: "john@email.com", phone: "6281234567890" },
  500000,
  "Clean Water Project"
);
```

## Event Ticketing

### Multiple Ticket Types

```bash
mcporter call mayar.create_invoice \
  name="Attendee Name" \
  email="attendee@email.com" \
  mobile="\"6281234567890\"" \
  description="Tech Conference 2026 Tickets" \
  redirectURL="https://event-site.com/tickets" \
  expiredAt="2026-03-01T23:59:59+07:00" \
  items='[
    {"quantity":2,"rate":500000,"description":"Early Bird Ticket"},
    {"quantity":1,"rate":150000,"description":"Workshop Add-on"}
  ]'
```

Total: Rp 1,150,000 (2×500K + 1×150K)

### Post-Payment Ticket Delivery

```javascript
pollPayment(invoiceId, async (paidInvoice) => {
  // Generate QR code tickets
  const tickets = await generateTickets(paidInvoice);
  
  // Send tickets via WhatsApp
  tickets.forEach((ticket, index) => {
    message({
      action: 'send',
      channel: 'whatsapp',
      target: paidInvoice.customer.mobile,
      message: `
🎟️ *Ticket ${index + 1}*

Event: Tech Conference 2026
Date: 15 March 2026
Venue: JCC Hall A

Scan QR code at entrance:
${ticket.qrCodeUrl}

See you there! 🎉
      `.trim()
    });
  });
});
```

## Analytics & Reporting

### Daily Revenue Report

```javascript
const today = execSync(`
  mcporter call mayar.get_transactions_by_time_period \
    page:1 pageSize:100 \
    period:"today" \
    sortField:"createdAt" \
    sortOrder:"DESC" \
    --output json
`);

const transactions = JSON.parse(today).data;
const revenue = transactions.reduce((sum, t) => sum + t.amount, 0);
const count = transactions.length;

const report = `
📊 *Daily Revenue Report*
Date: ${new Date().toLocaleDateString('id-ID')}

💰 Total Revenue: Rp ${revenue.toLocaleString('id-ID')}
📦 Transactions: ${count}
💵 Average: Rp ${Math.round(revenue / count).toLocaleString('id-ID')}

Top 5 Sales:
${transactions.slice(0, 5).map(t => 
  `• ${t.paymentLinkDescription}: Rp ${t.amount.toLocaleString('id-ID')}`
).join('\n')}
`.trim();

// Send to admin
message({
  action: 'send',
  channel: 'whatsapp',
  target: '+628xxxx', // Admin number
  message: report
});
```

### Monthly Summary

```bash
mcporter call mayar.get_transactions_by_time_period \
  page:1 pageSize:1000 \
  period:"this_month" \
  sortField:"amount" \
  sortOrder:"DESC"
```

## Error Handling

### Retry Failed Invoices

```javascript
function createInvoiceWithRetry(data, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const invoice = execSync(`
        mcporter call mayar.create_invoice \
          name="${data.name}" \
          email="${data.email}" \
          mobile="\\"${data.mobile}\\"" \
          description="${data.description}" \
          redirectURL="${data.redirectURL}" \
          expiredAt="${data.expiredAt}" \
          items='${JSON.stringify(data.items)}' \
          --output json
      `);
      
      return JSON.parse(invoice);
    } catch (error) {
      console.error(`Attempt ${i + 1} failed:`, error.message);
      if (i === maxRetries - 1) throw error;
      
      // Wait before retry (exponential backoff)
      await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, i)));
    }
  }
}
```

### Handle Expired Invoices

```javascript
function recreateExpiredInvoice(oldInvoiceId) {
  // Get old invoice details
  const unpaid = execSync(`
    mcporter call mayar.get_latest_unpaid_transactions page:1 pageSize:100 --output json
  `);
  
  const oldInvoice = JSON.parse(unpaid).data.find(t => t.id === oldInvoiceId);
  
  if (!oldInvoice) {
    throw new Error('Invoice not found');
  }
  
  // Create new invoice with same details but new expiry
  const newExpiry = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();
  
  return createInvoice({
    name: oldInvoice.paymentLinkName,
    email: oldInvoice.customer.email,
    mobile: oldInvoice.customer.mobile,
    description: oldInvoice.paymentLinkDescription,
    expiredAt: newExpiry,
    items: oldInvoice.items // Extract from original
  });
}
```

## Best Practices

### 1. Always Store Invoice IDs
```javascript
// Store mapping: customer → invoice ID
const invoiceDB = {
  [customerPhone]: {
    invoiceId: result.data.id,
    transactionId: result.data.transactionId,
    createdAt: Date.now(),
    status: 'pending'
  }
};
```

### 2. Set Reasonable Expiry Times
```javascript
// For immediate purchases: 24 hours
const expiry24h = new Date(Date.now() + 24 * 60 * 60 * 1000);

// For orders: 7 days
const expiry7d = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);

// For invoices: 30 days
const expiry30d = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
```

### 3. Format Phone Numbers Correctly
```javascript
function formatPhoneForMayar(phone) {
  // Remove all non-digits
  let cleaned = phone.replace(/\D/g, '');
  
  // Add country code if missing
  if (!cleaned.startsWith('62')) {
    cleaned = '62' + cleaned.replace(/^0+/, '');
  }
  
  return cleaned;
}
```

### 4. Handle Timezone Correctly
```javascript
// Always use Jakarta timezone for Indonesian customers
const expiry = new Date();
expiry.setDate(expiry.getDate() + 7);
const expiryISO = expiry.toISOString().replace('Z', '+07:00');
```
