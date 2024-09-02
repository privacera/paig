import React from 'react'
import {render} from 'react-dom';
import { HashRouter } from 'react-router-dom';

import 'import_common_files';
import stores from 'data/stores/all_stores';
import Root from 'root';

render(
  <HashRouter>
    <Root stores={stores} />
  </HashRouter>,
  document.getElementById('main_region')
);
