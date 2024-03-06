#/bin/bash
sudo apt-get update -y
sudo apt-get install python3 -y 
sudo apt-get install python3-pip -y 
sudo apt-get install python-is-python3 -y 

pip install streamlit==1.30.0
pip install python-dotenv==1.0.0
pip install openai==1.12.0

git clone https://github.com/SeryioGonzalez/AzureOpenAI_Assistants.git /home/streamlit/AzureOpenAI_Assistants

wget -O /etc/systemd/system/streamlit_app.service https://raw.githubusercontent.com/SeryioGonzalez/AzureOpenAI_Assistants/main/infrastructure/streamlit.service
sudo systemctl daemon-reload
sudo systemctl enable streamlit_app.service
sudo systemctl start streamlit_app.service