# asset-manager
Python application to analyze portfolio of assets and generate statistics and forecasts


## project setup
Below details the steps needed to get the project working on your machine

Note - Asset Manager utilizes MongoDB, so you will need to create a database connection (free)  
Note - Asset Manager utilizes finnhub.io, so you will need to create an account and get an API key (free)
- ```git clone https://github.com/anikolaj/asset-manager.git```
- run command ```git update-index --assume-unchanged asset_manager/config.yml```
- update asset_manager/config.yml with the database connection and finnhub.io API key details
- run the application with the command ```make run```
- run the unit tests with ```make test```