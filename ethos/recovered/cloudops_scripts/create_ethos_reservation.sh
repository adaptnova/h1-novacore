#!/bin/bash
# Script to create a reservation for the Ethos server
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

echo "Reservation created successfully."