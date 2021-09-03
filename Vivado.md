# Vivado Installation
## Windows
Run the **xsetup.exe** file from the setup folder as an administrator. During installation select the **Vivado HL WebPACK**.
## Linux
 - **Only for ubuntu users**: Run the following two commands in terminal.

	    sudo apt-get install libncurses5
        sudo apt-get install libtinfo5

 - Open the terminal in the setup folder and type the following command.
 
		sudo bash xsetup

 - The Xilinx installation window will open. Accept the license agreements and then select **Vivado HL WebPACK** edition for installation and go to the next window. In the **Design tools** check the **Vivado Design Suite** checkbox.
 - In the next window set the installation director. By default the installer will install the software in the **/opt/Xilinx** directory. But this can be changed. But make sure you know about the installation directory.
 - After that review the installation summary and then install.
 - After installation is complete, open the terminal and open the **.bashrc** file using the following instruction.
 
	    cd
	    vim ~/.bashrc
	You can use any other text editor instead of vim.
	

 - The above commands will open the **.bashrc** file. Navigate to the end of the file and add the following commands.

		source /opt/Xilinx/Vivado/2018.2/settings64.sh
	In case you changed installation directory instead of the default one then replace the **/opt/Xilinx** with that installation directory path.

 
 

 - For installing the cable drivers type the following command on terminal.
		 
		sudo bash /opt/Xilinx/Vivado/2018.2/data/xicom/cable_drivers/lin64/install_script/install_drivers/install_drivers
	
	In case you changed installation directory instead of the default one then replace the **/opt/Xilinx** with that installation directory path.

- Open a new terminal and type the following command to run vivado.
 
   		vivado

   



