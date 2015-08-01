

#setup_bash.sh
curl -k https://raw.githubusercontent.com/jshiv/stencil/master/scripts/setup/setup_bash.sh -o setup_bash.sh
sh setup_bash.sh
rm setup_bash.sh

#get_anaconda.sh
curl -k https://raw.githubusercontent.com/jshiv/stencil/master/scripts/setup/get_anaconda.sh -o get_anaconda.sh
sh get_anaconda.sh
rm get_anaconda.sh

#setup_env.sh
curl -k https://raw.githubusercontent.com/jshiv/stencil/master/scripts/setup/setup_env.sh -o setup_env.sh
sh setup_env.sh
rm setup_env.sh

# get_htop.sh
curl -k https://raw.githubusercontent.com/jshiv/stencil/master/scripts/setup/get_htop.sh -o get_htop.sh
sh get_htop.sh
rm get_htop.sh

git clone https://github.com/jshiv/root.git
