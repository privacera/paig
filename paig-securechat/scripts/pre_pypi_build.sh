DATA_DIR="data"
UI_BUILD_DIR="web-ui/build"
WEB_SERVER_DIR="web-server/src/paig_securechat"


function create_ui_bild() {
  echo "Delete existing UI build"
  rm -rf $UI_BUILD_DIR
  echo "Building UI"
  echo "Installing npm version 9.8.1"
  npm install npm@9.8.1 -g
  cd web-ui || { echo "Error: web-ui directory not found"; return 1; }
  echo "Installing dependencies"
  npm install --legacy-peer-deps
  npm run build
  echo "Removing node_modules"
  rm -rf node_modules
  npm cache clean --force
  cd ..
  echo "UI build completed"
}


function delete_ui_build() {
  echo "Delete created UI build after copying to templates folder"
  rm -rf $UI_BUILD_DIR
}



function copy_data() {
  echo "Remove existing data files from the package"
  rm -rf $WEB_SERVER_DIR/data/*
  echo "Creating data folder"
  mkdir -p $WEB_SERVER_DIR/data
  echo "Copying data files to the package"
  cp -r  $DATA_DIR/* $WEB_SERVER_DIR/data/

}


function copy_ui_build_to_templates_folder() {
  echo "Remove existing UI build from templates folder"
  rm -rf $WEB_SERVER_DIR/templates/*
  echo "Creating templates folder"
  mkdir -p $WEB_SERVER_DIR/templates
  echo "Copying UI build to templates folder"
  cp -r $UI_BUILD_DIR/* $WEB_SERVER_DIR/templates/
}

function main() {
  copy_data
  create_ui_bild
  copy_ui_build_to_templates_folder
  delete_ui_build
}

main $@
