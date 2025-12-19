# IBM Cloud Quota Increase Request

## Current Situation

We're trying to create a reservation for the Ethos server with the following configuration:
- Profile: gx3-48x240x2l40s (48 vCPUs)
- Zone: us-south-1
- Resource group: adapt
- Affinity policy: automatic
- Term: 3 years
- Expiration policy: renew

However, we're encountering the following error:
```
Error code: bad_field
Error message: requested reservation 1 of gx3-48x240x2l40s - this request will put the account over: vCPU quota, -requested total vCPUs: 216 > quota vCPUs: 200;
```

## Quota Increase Request Process

To request a quota increase for your IBM Cloud account, follow these steps:

1. **Log in to IBM Cloud Console**:
   - Go to [IBM Cloud Console](https://cloud.ibm.com/)
   - Log in with your IBM Cloud credentials

2. **Navigate to Quotas & Limits**:
   - Click on "Manage" in the top navigation
   - Select "Account" from the dropdown
   - Click on "Quotas and limits" in the left sidebar

3. **Request a Quota Increase**:
   - Find the "Virtual Server for VPC" section
   - Locate the vCPU quota for the us-south region
   - Click on "Request increase"
   - Fill out the form with the following information:
     - Current quota: 200 vCPUs
     - Requested quota: 250 vCPUs (or more as needed)
     - Justification: "Need to create a reservation for an existing gx3-48x240x2l40s instance (Ethos server) with 48 vCPUs. Current DataOps reservations use 24 vCPUs. Total required: 72 vCPUs for reservations."
     - Business impact: "Critical for production environment. Need to optimize costs with 3-year reservations."

4. **Submit the Request**:
   - Review the information
   - Submit the request
   - IBM Cloud support will review your request and respond, typically within 1-2 business days

5. **Alternative Contact Method**:
   - Open a support ticket with IBM Cloud Support
   - Provide the same information as above
   - Request expedited processing if urgent

## Temporary Workaround

While waiting for the quota increase, you can:

1. Continue using the Ethos server without a reservation
2. The DataOps servers already have active reservations
3. Once the quota increase is approved, create the Ethos reservation

## Note on Quota vs. Usage

It's important to understand that the quota is a limit on what you can reserve or provision, not what you're actually using. Even though you already have the Ethos server running, creating a reservation for it requires additional quota capacity.