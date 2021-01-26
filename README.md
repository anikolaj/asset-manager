# asset-manager
Python application to analyze portfolio of assets and generate statistics and forecasts


## project setup
Below details the steps needed to get the project working on your machine

Note - Asset Manager utilizes MongoDB, so you will need to create a database connection (free)  
Note - Asset Manager utilizes finnhub.io, so you will need to create an account and get an API key (free)
- ```git clone https://github.com/anikolaj/asset-manager.git```
- Run command ```git update-index --assume-unchanged asset_manager/config.yml```
- Update asset_manager/config.yml with the database connection and finnhub.io API key details
- Run the application with the command ```make run PORTFOLIO=$portfolioName``` where ```$portfolioName``` is the name of the portfolio you wish to track
	- Note - if this is the first time running with the specified portfolio name, the app will walk you through portfolio setup
- run the unit tests with ```make test```