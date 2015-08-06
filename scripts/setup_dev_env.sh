DEV_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../.. && pwd )"


REPO="${DEV_PATH}/stencil/stencil " 


function HIGHLIGHT {
    echo "$(tput setaf 2)$1$(tput sgr0)"
}

function CLEAN_AND_CONTINUE {
	if [ -d "${1}" ]; then
		echo "... FOUND EXISTING DIRECTORY AT ${1}"
		while true; do
			read -p "... DO YOU WISH TO REMOVE ${1} AND CONTINUE WITH DEPLOYMENT (Y/N)?" yn
			case $yn in
				[Yy]* ) echo "... REMOVING ${1}"; rm -rf ${1}; break;;              
				[Nn]* ) echo "... ABORTING DEPLOYMENT";  return;;
				* ) echo "... PLEASE ANSWER YES OR NO.";;
			esac
		done
	fi
}

HIGHLIGHT "> SETTING UP stencil IN ${DEV_PATH}" 
HIGHLIGHT "> ====================================================="

HIGHLIGHT "> SETTING UP VIRTUAL ENVIRONMENT stencil"
CLEAN_AND_CONTINUE ${DEV_PATH}/stencil/env

virtualenv --no-site-packages ${DEV_PATH}/stencil/env
echo "... VIRTUAL ENV faro ADDED TO ${DEV_PATH}/stencil/env"


HIGHLIGHT "> SETTING UP ENVIRONMENT"
. ${DEV_PATH}/stencil/env/bin/activate

HIGHLIGHT "> INSTALLING stencil"
# The following packages, which can be temperamental to install, seem to do better if explicitly 
# installed.
pip install numpy
pip install pandas
sudo pip install -e ${DEV_PATH}/stencil

# RUN TESTS
HIGHLIGHT "> TESTING ENVIRONMENT"
python ${DEV_PATH}/stencil/scripts/test_env.py
