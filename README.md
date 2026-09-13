# tjp-public-repo

Just stuff I am learning/working on to show employers I am capable of what I say I can do. 

AI is used to create the website itself, I am not a web developer and not planning to be one, so it was quicker to use AI to develop it than learn.

I will be learning and writing python myself as its used a lot in cloud/infrastructure roles, eventually I'll move my AWS terraform code here to show the TF stuff I built for my own AWS account, I do not keep things running there because I have no desire to pay a monthly cost which will add up.

All secrets are encrypted via SOPs and age encryption, age is used over pgp due to simplicity and speed in setting up over the more complex pgp.

## Website deployment

The website is deployed to my RKE2 Kubernetes cluster using ArgoCD.

- `deploy/argocd/thejammyproject.yaml` registers the website with ArgoCD and tells it to monitor this repository.
- `deploy/k8s/thejammyproject/current-site.yaml` defines the website containers, internal service, TLS cert, ingress and network policy.

When the Kubernetes manifest changes on the main branch, ArgoCD automatically applies the change and keeps the cluster synchronized with GitHub. The ArgoCD manifest is normally only needed when initially registering or recreating the application.
