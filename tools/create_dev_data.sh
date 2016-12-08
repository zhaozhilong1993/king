#!/biun/bash

USER_ID="c996d6bcc8ce4d1a93400d27c0c889a9"
RESOURCE_ID="1234567"
PROJECT_ID="1205fa6ec43b482db11f43ad6eeed802"
PRICE_ID="e16f9622-60a5-4d93-a33b-7ba112eaa3f5"


#king --debug account-create c996d6bcc8ce4d1a93400d27c0c889a9
king --debug price-create --resource_type disk --order_type time --resource_id $RESOURCE_ID 10
#king --debug order-create --resource_id $RESOURCE_ID --price_id ${PRICE_ID} --order_type disk $PROJECT_ID

#openstack role create payer
#openstack role add --user c996d6bcc8ce4d1a93400d27c0c889a9 --project services payer
