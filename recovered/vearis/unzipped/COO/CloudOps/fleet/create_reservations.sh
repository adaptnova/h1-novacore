#!/bin/bash
# Script to create reservations for IBM Cloud instances
# Created: 2025-03-22
# Author: Zorion (IBM Cloud Strategist & Provisioning Engineer)

# Resource group
RESOURCE_GROUP="adapt"

# Create reservation for Ethos server
echo "Creating reservation for Ethos server..."
ibmcloud is reservation-create \
  --name ethos-reservation \
  --capacity 1 \
  --term three_year \
  --profile gx3-48x240x2l40s \
  --profile-resource-type instance_profile \
  --zone us-south-1 \
  --affinity-policy automatic \
  --expiration-policy renew \
  --resource-group-name $RESOURCE_GROUP

# Create reservation for dataops-primary server
echo "Creating reservation for dataops-primary server..."
ibmcloud is reservation-create \
  --name dataops-primary-reservation \
  --capacity 1 \
  --term three_year \
  --profile bx2-8x32 \
  --profile-resource-type instance_profile \
  --zone us-south-1 \
  --affinity-policy automatic \
  --expiration-policy renew \
  --resource-group-name $RESOURCE_GROUP

# Create reservation for dataops-timeseries server
echo "Creating reservation for dataops-timeseries server..."
ibmcloud is reservation-create \
  --name dataops-timeseries-reservation \
  --capacity 1 \
  --term three_year \
  --profile bx2-8x32 \
  --profile-resource-type instance_profile \
  --zone us-south-1 \
  --affinity-policy automatic \
  --expiration-policy renew \
  --resource-group-name $RESOURCE_GROUP

# Create reservation for dataops-vector server
echo "Creating reservation for dataops-vector server..."
ibmcloud is reservation-create \
  --name dataops-vector-reservation \
  --capacity 1 \
  --term three_year \
  --profile bx2-8x32 \
  --profile-resource-type instance_profile \
  --zone us-south-1 \
  --affinity-policy automatic \
  --expiration-policy renew \
  --resource-group-name $RESOURCE_GROUP

echo "Reservations created successfully."