#########################################################################################################
To run test cases for any WAF/RASP instances with logs:
       0. Download the waf_attack_scripts.py & rasp_attack_scripts.py from our git
       1. ssh to the corresponding WAF/RASP instance and create a folder under /home/ubuntu/ using:
          sudo mkdir /home/ubuntu/attack_scripts
       2. Assign the full access to the folder using:
          sudo chmod 777 /home/ubuntu/attack_scripts
       3. cd in to the folder and then create a new file using:
          cd /home/ubuntu/attack_scripts
          sudo vi attack_scripts.py
          - Then copy all the code from our git's rasp_attack_scripts.py/waf_attack_scripts.py to this new file and save
       4. Run the code using:
          python rasp_attack_scripts.py - if you are testing rasp
          python rasp_attack_scripts.py - if you are testing waf
       5. Enter the name of WAF/RASP you want to test with the instructions. Then Enter "YES"
       6. After testing is done, a "Testing End..." message will be shown. Then a .csv file is 
          created under the same folder.
       7. Download the .csv to your machine using ftp tool (e.g filezilla in windows, cyberduck in mac)
       8. Open the .csv file to check the testing results

#########################################################################################################
To run test cases for any WAF/RASP instances WITHOUT logs:
       0. Download the waf_attack_scripts.py & rasp_attack_scripts.py from our git
       1. Run the code using:
          python rasp_attack_scripts.py - if you are testing rasp
          python rasp_attack_scripts.py - if you are testing waf
       2. Enter the name of WAF/RASP you want to test with the instructions. Then Enter "NO"
       3. After testing is done, a "Testing End..." message will be shown. 
       4. Then, please check the dashboard or other sources that can shows the detection of attacks.