# Nova Instance Templates
Date: February 13, 2025 19:46 MST
Author: V.I. (Vaeris Intelligence)

## Standard Instance Creation Template
```bash
# Create instance with pre-configured disks
gcloud compute instances create [INSTANCE_NAME] \
    --project=a-d-a-p-t \
    --zone=us-central1-a \
    --machine-type=c3-highcpu-44 \
    --network-interface=ipv6-network-tier=PREMIUM,network-tier=PREMIUM,nic-type=GVNIC,stack-type=IPV4_IPV6,subnet=nova-1500-1-subnet \
    --network-interface=ipv6-network-tier=PREMIUM,network-tier=PREMIUM,nic-type=GVNIC,stack-type=IPV4_IPV6,subnet=nova-1500-2-subnet \
    --network-interface=ipv6-network-tier=PREMIUM,network-tier=PREMIUM,nic-type=GVNIC,stack-type=IPV4_IPV6,subnet=nova-1500-3-subnet \
    --network-interface=ipv6-network-tier=PREMIUM,network-tier=PREMIUM,nic-type=GVNIC,stack-type=IPV4_IPV6,subnet=nova-1500-4-subnet \
    --network-interface=ipv6-network-tier=PREMIUM,network-tier=PREMIUM,nic-type=GVNIC,stack-type=IPV4_IPV6,subnet=nova-8896-5-sub-central1 \
    --network-interface=ipv6-network-tier=PREMIUM,network-tier=PREMIUM,nic-type=GVNIC,stack-type=IPV4_IPV6,subnet=nova-8896-6-sub-central1 \
    --network-interface=ipv6-network-tier=PREMIUM,network-tier=PREMIUM,nic-type=GVNIC,stack-type=IPV4_IPV6,subnet=nova-8896-7-sub-central1 \
    --network-interface=ipv6-network-tier=PREMIUM,network-tier=PREMIUM,nic-type=GVNIC,stack-type=IPV4_IPV6,subnet=nova-8896-8-sub-central1 \
    --no-restart-on-failure \
    --maintenance-policy=TERMINATE \
    --provisioning-model=SPOT \
    --instance-termination-action=STOP \
    --service-account=231017561254-compute@developer.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=https-server,http-server,allow-iap,chrome-remote,nova-net,vscode-remote \
    --disk=boot=yes,device-name=boot-[NAME],mode=rw,name=boot-[NAME] \
    --disk=boot=no,device-name=data-[NAME],mode=rw,name=data-[NAME] \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=goog-ec-src=vm_add-gcloud \
    --reservation-affinity=any \
    --network-performance-configs=total-egress-bandwidth-tier=TIER_1

# Example for adapt server:
gcloud compute instances create adapt \
    [same options as above] \
    --disk=boot=yes,device-name=boot-adapt,mode=rw,name=boot-adapt \
    --disk=boot=no,device-name=data-adapt,mode=rw,name=data-adapt \
    [rest of options]
```

## Server-Specific Notes

### Adapt Server
- Boot disk: boot-adapt
- Data disk: data-adapt
- Primary role: Infrastructure & Database Operations
- Networks: 4x 1500 MTU + 4x 8896 MTU

### Ethos Server
- Boot disk: boot-ethos
- Data disk: data-ethos
- Primary role: ML Operations & Model Training
- Networks: 4x 1500 MTU + 4x 8896 MTU

### Vaeris Server
- Boot disk: boot-vaeris
- Data disk: novas-vaeris
- Primary role: Network Operations & System Management
- Networks: 4x 1500 MTU + 4x 8896 MTU

## Key Features
- GVNIC for all network interfaces
- IPv4 + IPv6 dual stack
- PREMIUM tier networking
- Spot instances for cost optimization
- IAP-enabled for secure access
- Hyperdisk volumes for performance
- Full mesh network topology

## Important Notes
- Always specify both boot and data disks in initial creation
- Use consistent naming pattern: boot-[name] and data-[name]
- All instances use same network configuration
- All instances are spot/preemptible for cost efficiency
- All instances have IAP access configured