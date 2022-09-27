# Multi-agents for Online Social Networks in Urban planning

In this code, a model can be run to test the effect of different variables.
First the data have to prepared using the method *scrape_data.py* to scrape the data. 
Then general analysis over this data can be done using the file *preprocess_population.py*.
Next, user information to initialize the agents is used. 
First, the network structure (*preprocess_network.py*) has to be obtained and 
after the individual characteristics are obtained (*preprocess_individual.py*).

To run the simulation the function *run.py* have to be run.
A window will open and the different variables can be examined.
When running the simulation simultanuously a CSV is created saving 
for each time step the states of the agents and the number of tweets. 
With the file *compute_score* the score can be computed and with *plot_data.py* the plots can be saved.
