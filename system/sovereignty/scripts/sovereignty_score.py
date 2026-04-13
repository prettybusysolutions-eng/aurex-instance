#!/usr/bin/env python3
import json, subprocess

def sh(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()

region='us-east-2'
ids=sh(f"aws ssm describe-instance-information --region {region} --query 'InstanceInformationList[].InstanceId' --output text").split()
score=0
checks=[]
if ids:
    score+=2; checks.append('ssm_managed')

# cloudwatch agent active check via command summary (best effort)
cmd=sh(f"aws ssm send-command --region {region} --document-name AWS-RunShellScript --instance-ids {' '.join(ids)} --parameters commands='[\"systemctl is-active amazon-cloudwatch-agent || true\",\"systemctl is-active fail2ban || true\",\"ufw status | head -n1 || true\"]' --query 'Command.CommandId' --output text")
_ = sh(f"sleep 4; aws ssm list-command-invocations --region {region} --command-id {cmd} --query 'CommandInvocations[].Status' --output text")
out=sh(f"aws ssm list-command-invocations --region {region} --command-id {cmd} --details --query 'CommandInvocations[].CommandPlugins[0].Output' --output text")
if 'active' in out:
    score+=3; checks.append('agents_active')
if 'Status: active' in out:
    score+=2; checks.append('ufw_active')

# alarms count
alarms=int(sh("aws cloudwatch describe-alarms --region us-east-2 --query 'length(MetricAlarms[])' --output text"))
if alarms>=8:
    score+=3; checks.append('alarms')

print(json.dumps({'score_10':round(min(10,score),1),'checks':checks,'managed_instances':ids,'alarms':alarms}))
