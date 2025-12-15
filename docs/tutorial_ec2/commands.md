startare container con localstack-pro

# create ec2 key pair for ssh

awslocal ec2 create-key-pair \
    --key-name my-key \
    --query 'KeyMaterial' \
    --output text | tee key.pem


Apply the right permissions to the file with this command:

chmod 400 key.pem

Add inbound roles:
In LocalStack, networking features like subnets and VPCs are not emulated. LocalStack provides a default security group that manages the exposed ports for the EC2 instance. While users can create additional security groups, LocalStack focuses on the default security group.

By default, the SSH port 22 is open. To enable inbound traffic on the port 8000 for our Flask API, use this command to authorize the default security group:

awslocal ec2 authorize-security-group-ingress \
    --group-id default \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0


Retrieve the security group ID with this command:

sg_id=$(awslocal ec2 describe-security-groups | jq -r '.SecurityGroups[0].GroupId')
echo $sg_id

Now, you can start and operate the EC2 instance on your local machine. Before executing the command, create a new file named user_script.sh with commands to install python and your app.

Now, directly initiate the EC2 instance by executing the following command:

# possiamo lanciare anche piu istanze cambiando il parametro --count
awslocal ec2 run-instances \
  --image-id ami-df5de72bdb3b \
  --count 1 \
  --instance-type t3.nano --key-name my-key \
  --security-group-ids $sg_id \
  --user-data file://./user_script.sh

After launching the EC2 instance, check the LocalStack logs. In these logs, you can confirm that the EC2 instance is running successfully on your local machine.

localstack logs
...
Determined main container network: bridge
Determined main container target IP: 172.17.0.2
Instance i-42e830289e675885f will be accessible 
via SSH at: 127.0.0.1:22, 172.17.0.3:22
Instance i-42e830289e675885f port mappings (container -> host): 
{'8000/tcp': 8000, '22/tcp': 22}
AWS ec2.RunInstances => 200


In the logs above, verify that the instance is accessible via SSH at 127.0.0.1. Depending on your setup, this configuration might change. In this example, you can use the following command to log in to the EC2 instance:

ssh -i key.pem root@127.0.0.1

In the local EC2 instance, you can execute various commands, similar to a real EC2 instance on the AWS cloud. You can also use cURL to confirm if your Flask API is operational:

root@6ef2a4c8d8ac:~# curl localhost:8000 
Hello, LocalStack!

In the LocalStack logs, confirm that the port mappings from the container to the host are accessible on port 8000. Run the following command in a separate terminal tab to check if the Flask API is reachable:

curl localhost:8000
Hello, LocalStack!
Additionally, send GET and POST requests to test the active Flask API:

curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"key": "value"}' \
    localhost:8000/post
This is a POST request example. Received data: {'key': 'value'}

curl http://localhost:8000/get
This is a GET request example.

# Tutorial ELB Docs Localstack 

elb verso ec2 in docker container non funziona, o meglio funziona solo utilizzando un target group di tipo ip, quindi cosi si riesce, mandando una richiesta al load balancer, a raggiungere una istanza ec2, ma funziona solo raggiungendo la prima istanza registrata nel gruppo, se l'istanza viene fermata (tramite aws cli o docker container stoppato), con il target group di tipo ip non scatta il meccanismo di failover automatico verso la seconda istanza come ci si aspetterebbe. Questo accade perché, quando il container viene arrestato, il suo indirizzo IP viene rimosso fisicamente dalla tabella di routing della rete Docker, causando un errore immediato di tipo "No Route to Host" quando il Load Balancer tenta la connessione; il sistema di emulazione di LocalStack non interpreta correttamente questa eccezione di rete come un fallimento standard del controllo di integrità (Health Check), rimanendo quindi bloccato nel tentativo di inviare traffico verso un indirizzo inesistente invece di marcarlo come "Unhealthy" e deviare le richieste verso l'unica istanza rimasta attiva.

Non possiamo risolvere cambiando il target group da ip a 'instance', poichè anche se la registrazione va a buon fine, il load balancer non riesce a raggiungere l'istanza ec2, probabilmente per problemi di networking interni a docker container che impediscono il corretto instradamento del flusso dati tra il servizio ALB simulato e il container dell'istanza, infatti ricevevamo sempre un payload vuoto nelle richieste http inoltrate.


non funziona nemmeno il tutorial dalla docs su elb!.


 morale della favola in locale possiamo usare le ec2 per fare dei test tramite ssh o http, ma non possiamo metterle dietro un load balancer simulato in localstack.