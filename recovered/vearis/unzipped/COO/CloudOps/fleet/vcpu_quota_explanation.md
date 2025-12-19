# vCPU Quota Explanation for IBM Cloud Reservations

## What Happened

When we tried to create a reservation for the Ethos server with the profile `gx3-48x240x2l40s`, we received this error:

```
Error code: bad_field
Error message: requested reservation 1 of gx3-48x240x2l40s - this request will put the account over: vCPU quota, -requested total vCPUs: 240 > quota vCPUs: 200;
```

## Understanding vCPU Quotas

### What is a vCPU Quota?

A vCPU quota is a limit set by IBM Cloud on the total number of virtual CPUs (vCPUs) that an account can reserve or use at one time. This is a resource management mechanism to ensure fair distribution of compute resources across all IBM Cloud customers.

### Your Current Situation

- **Your account's vCPU quota**: 200 vCPUs
- **Ethos server profile**: gx3-48x240x2l40s (48 vCPUs)
- **DataOps servers**: 3 x bx2-8x32 (8 vCPUs each, total 24 vCPUs)
- **Total vCPUs already reserved**: 24 vCPUs (for DataOps servers)
- **Remaining quota available**: 176 vCPUs (200 - 24)

### The Issue

The Ethos server profile (gx3-48x240x2l40s) requires 240 vCPUs for a reservation, which exceeds your account's quota of 200 vCPUs. Even if you had no other reservations, this single reservation would exceed your quota.

## Options to Resolve This

1. **Request a Quota Increase**:
   - Contact IBM Cloud support to request an increase to your vCPU quota
   - This is the best option if you need the exact profile (gx3-48x240x2l40s)

2. **Choose a Smaller Profile**:
   - Select a GPU-enabled profile with fewer vCPUs
   - Options from the list we found:
     - gx3-24x120x1l40s (24 vCPUs, 1 L40S GPU)
     - gx3-16x80x1l4 (16 vCPUs, 1 L4 GPU)
     - gx2-32x256x2v100 (32 vCPUs, 2 V100 GPUs)

3. **Split the Reservation**:
   - Create multiple smaller reservations that together provide similar capacity
   - For example, two gx3-24x120x1l40s reservations instead of one gx3-48x240x2l40s

4. **Use On-Demand Without Reservation**:
   - Continue using the Ethos server without a reservation
   - You'll still benefit from the DataOps reservations
   - This means no long-term commitment or discount for the Ethos server

## Recommendation

Since the Ethos server is already running with the gx3-48x240x2l40s profile, the most practical approach is:

1. **Short-term**: Continue using the Ethos server without a reservation
2. **Long-term**: Request a quota increase from IBM Cloud support

This allows you to maintain your current setup while working toward getting the appropriate reservation in place.