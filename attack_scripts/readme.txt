#########################################################################################################
To run test cases for any WAF instances:
       1. ssh to the corresponding WAF instance and create a folder under /home/ubuntu/ using:
          sudo mkdir /home/ubuntu/attack_scripts
       2. Assign the full access to the folder using:
          sudo chmod 777 /home/ubuntu/attack_scripts
       3. cd in to the folder and then create a new file using:
          cd /home/ubuntu/attack_scripts
          sudo vi attack_scripts.py
          (Then just copy all the code from our git's attack_scripts.py to this new file and save)
       4. Run the code using:
          python attack_scripts.py
       5. Enter the name of WAF you want to test with the instructions.
       6. After testing is done, a "Testing End..." message will be shown. Then a .csv file is 
          created under the same folder.
       7. Download the .csv to your machine using ftp tool (e.g filezilla in windows, cyberduck in mac)
       8. Open the .csv file to check the testing results