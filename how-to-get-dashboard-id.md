# How to Get Your Metabase Dashboard ID

## Step 1: Find Your Dashboard URL
1. Open your dashboard in Metabase
2. Look at the URL in your browser
3. It should look like: `http://localhost:3000/dashboard/12345`
4. The number at the end (12345) is your Dashboard ID

## Step 2: Update the HTML File
1. Open `metabase-dashboard.html`
2. Find this line:
   ```html
   <iframe src="http://localhost:3000/dashboard/YOUR_DASHBOARD_ID">
   ```
3. Replace `YOUR_DASHBOARD_ID` with your actual dashboard ID

## Step 3: Enable Public Sharing (Optional)
If you want to share without login:
1. Go to your dashboard
2. Click "Share" button
3. Enable "Public sharing"
4. Copy the public link
5. Use that URL in the iframe instead

## Step 4: Open Your Custom Dashboard
1. Double-click `metabase-dashboard.html`
2. It will open in your browser with custom styling
3. You'll see your Metabase dashboard with the modern CSS wrapper

## Features of This Custom CSS:
- ✅ Dark gradient background
- ✅ Glass morphism effects
- ✅ Modern typography (Inter font)
- ✅ Responsive design
- ✅ Metric badges with icons
- ✅ Insights panel
- ✅ Rounded corners and shadows
- ✅ Mobile-friendly
