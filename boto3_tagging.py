import boto3
import collections
import datetime
import time
import re

ec = boto3.client('ec2')

def lambda_handler(event, context):
    retention_days = 7
    delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
    delete_fmt = delete_date.strftime('%Y-%m-%d')
    #delete_fmt = 'testtesttest'

    print '---'
    print "Looking to tag snaps with DeleteOn date: %s" % (delete_fmt)
    snapshots = ec.describe_snapshots(
        Filters=[
            {'Name': 'tag-key', 'Values': ['DeleteOn']},
            {'Name': 'tag-value', 'Values': ['%s' % (delete_fmt)]},
        ]
    ).get(
        'Snapshots', []
    )

    snaps = []
    for s in snapshots:
        snaps.append(s['SnapshotId'])
    print '---'
    print "Found %d snaps to tag." % len(snaps)
    for snap in snaps:
        snap_id = ec.describe_snapshots(SnapshotIds=(snap,)).get('Snapshots')[0]['SnapshotId']
        print '---'
        print snap_id

        vol_id = ec.describe_snapshots(SnapshotIds=(snap,)).get('Snapshots')[0]['VolumeId']
        print vol_id

        vol_dev = ec.describe_volumes(VolumeIds=(vol_id,)).get('Volumes')[0]['Attachments'][0]['Device']
        print vol_dev

        inst_id = ec.describe_volumes(VolumeIds=(vol_id,)).get('Volumes')[0]['Attachments'][0]['InstanceId']
        print inst_id

        inst_name = ''
        inst_tags = ec.describe_instances(InstanceIds=(inst_id,)).get('Reservations')[0]['Instances'][0]['Tags']
        for x in xrange(len(inst_tags)):
    #        print ec.describe_instances(InstanceIds=(inst_id,)).get('Reservations')[0]['Instances'][0]['Tags'][x]['Key']
            tag = ec.describe_instances(InstanceIds=(inst_id,)).get('Reservations')[0]['Instances'][0]['Tags'][x]['Key']
            if tag == 'Name':
                inst_name = ec.describe_instances(InstanceIds=(inst_id,)).get('Reservations')[0]['Instances'][0]['Tags'][x]['Value']
            else:
                continue
        print inst_name
        response = ec.create_tags(
    #        DryRun=True,
            Resources=(snap_id,),
            Tags=[
                {'Key': 'Instance ID', 'Value': inst_id},
                {'Key': 'Name', 'Value': inst_name},
                {'Key': 'Volume Device', 'Value': vol_dev},
            ]
        )
        print response
    print '---'
