
# DocumentCloud Add-On

[Please see the Add-On documentation](https://github.com/MuckRock/documentcloud-hello-world-addon/wiki/)

# Top Daily Docs Add-On

This repository contains a DocumentCloud Add-On that sends an email or Slack alert to the user every day which contains the top viewed documents on DocumentCloud in the last 24 hours. 

The Add-On calls a cURL command that is saved as an environment secret as the command contains three secrets and Add-Ons only support two. 

Below is the cURL command that it calls to engage with Cloudflare's GraphQL endpoint (querying for Web Analytics in particular) with the secrets redacted. 
Note that the Add-On also substitutes the start date to be the current day minus 1 day to capture information from the last 24 hours. 

- The AUTH_EMAIL should be the email address for the Cloudflare account with privileges to run the web analytics query. 

- The API_TOKEN should be replaced with the API token with privileges to read analytics and logs, which you can set up here:
https://dash.cloudflare.com/profile/api-tokens

- The ACCOUNT_ID shold be set to the ACCOUNT_ID of the service on Cloudflare, which you can see under the API subheader on the right sidebar when you click on the documentcloud.org site. 

```
curl 'https://api.cloudflare.com/client/v4/graphql' -H 'Accept-Encoding: gzip, deflate, br' -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Connection: keep-alive' -H 'Origin: altair://-' -H 'Authorization: Bearer API_TOKEN' -H 'X-AUTH-EMAIL: AUTH_EMAIL' --data-binary '{"query":"# Welcome to Altair GraphQL Client.\n# You can send your request using CmdOrCtrl + Enter.\n\n# Enter your graphQL query here.\n{\n  viewer {\n    accounts(filter: { accountTag: $tag }) {\n      rumPageloadEventsAdaptiveGroups(\n        filter: { datetime_gt: $start }\n        limit: 1000\n        orderBy: [sum_visits_DESC]\n      ) {\n        dimensions {\n          countryName\n          date\n          refererHost\n          refererPath\n          requestHost\n          requestPath\n        }\n        avg {\n          sampleInterval\n        }\n        sum {\n          visits\n        }\n        count\n      }\n    }\n  }\n}","variables":{"tag":"ACCOUNT_ID","start":"2025-03-04T00:00:00Z"}}' --compressed
```

When creating this Add-On, I found the following documentation useful as Cloudflare's was very sparse. 
https://boehs.org/node/notes-on-the-cloudflare-web-analytics-api
https://web.archive.org/web/20240504033446/https://boehs.org/node/notes-on-the-cloudflare-web-analytics-api

https://community.cloudflare.com/t/downloading-web-analytics-data/473295/4

For posterity, here is the full GraphQL command as well, which you can test on a local client like Altair. In the GraphQL client you will need to also set up authentication headers of X-AUTH-EMAIL and the Bearer token. 

```{
    viewer {
        accounts(filter: { accountTag: $tag }) {
            rumPageloadEventsAdaptiveGroups(
                filter: { datetime_gt: $start }
                limit: 10
                orderBy: [sum_visits_DESC]
            ) {
                dimensions {
                    countryName
                    date
                    refererHost
                    refererPath
                    requestHost
                    requestPath
                }
                avg {
                    sampleInterval
                }
                sum {
                    visits
                }
                count
            }
        }
    }
}

{
    "tag": "REDACTED",
    "start": "2025-02-10T00:00:00Z"
}
```