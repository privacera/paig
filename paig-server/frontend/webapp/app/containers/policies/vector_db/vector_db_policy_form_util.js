import { isEmpty, uniqBy, compact, uniq } from "lodash";
import { observable, action, ObservableMap } from "mobx";
import { PROMPT_REPLY_TYPE } from 'utils/globals';

class VectorDBPolicyFormUtil {
  @observable _vState = {
    editMode: false
  }

  errorListMap = new ObservableMap();
  restrictionMap = new ObservableMap();

  init = (form) => {
    this.form = form;
  }

  setNewPayloadInForm = (payload) => {
    this.setPayloadAsPerFormField(payload);
    this.form.clearForm();
    this.form.refresh({...payload});
    this.form.model = payload;
  }

  setPayloadAsPerFormField = (payload) => {
    this.restrictionMap.clear();
    const deny = [];
    const allow = [];
    const restriction = [];

    if (payload.allowedGroups?.[0] === 'public') {
      // payload.others = [];
      payload.allowedGroups = ['Everyone'];
    }
    if (payload.deniedGroups?.[0] === 'public') {
      // payload.others = [];
      payload.deniedGroups = ['Others'];
    }
  }

  getVState = () => {
    return this._vState;
  }

  getErrorHashMap = () => {
    return this.errorListMap;
  }

  getRestrictionMap = () => {
    return this.restrictionMap;
  }

  clearErrorHashMap = () => {
    this.errorListMap.clear();
  }

  getForm = () => {
    return this.form;
  }

  getFormData = () => {
    return this.form.toJSON();
  }

  setEditMode = (mode) => {
    this._vState.editMode = mode;
  }

  getFormMode = () => {
    return this._vState.editMode;
  }

  formValidation = async () => {
    await this.form.validate();
    const permissionValid = this.validatePermissions();
    return this.form.valid && permissionValid;
  }

  @action
  validatePermissions = () => {
    this.errorListMap.clear();

    const formData = this.getFormData()
    
    const allowedFieldNames = this.getPermissionErrorFieldKeys({
      ...formData,
      users: formData.allowedUsers,
      groups: formData.allowedGroups,
      roles: formData.allowedRoles
    }, 'allow');
    // const denyFieldNames = this.getPermissionErrorFieldKeys({
    //   ...formData,
    //   users: formData.deniedUsers,
    //   groups: formData.deniedGroups,
    //   roles: formData.deniedRoles
    // }, 'deny');
    
  const fieldNames = uniq([...allowedFieldNames/*, ...denyFieldNames*/])

    if (!isEmpty(fieldNames)) {
      if (Array.isArray(fieldNames)) {
        fieldNames.forEach(name => {
          this.errorListMap.set(name, name);
        })
      } else {
        this.errorListMap.set(fieldNames, fieldNames);
      }
    }

    return !this.errorListMap.size;
  }

  getPermissionErrorFieldKeys = (field, errorPath) => {
    const { ROLE_USER_GROUP, META_DATA } = this.getPermissionErrorTypes();
    const { roles=[], groups=[], users=[], others=[], metadataKey=[] } = field;
    const errorFieldNames = [];
    const isRequestSelected = true;
    if ((!roles.length && !groups.length && !users.length && !others.length) && !metadataKey && !isRequestSelected) {
      errorFieldNames.push(...[`${errorPath}${ROLE_USER_GROUP}`, META_DATA]);
    } else if ((roles.length || groups.length || users.length || others.length) && !metadataKey && !isRequestSelected) {
      errorFieldNames.push(...[META_DATA]);
    } else if ((!roles.length && !groups.length && !users.length && !others.length) && metadataKey && !isRequestSelected) {
      errorFieldNames.push(...[`${errorPath}${ROLE_USER_GROUP}`]);
    } else if ((!roles.length && !groups.length && !users.length && !others.length) && !metadataKey && isRequestSelected) {
      errorFieldNames.push(...[`${errorPath}${ROLE_USER_GROUP}`, META_DATA]);
    } else if ((roles.length || groups.length || users.length || others.length) && !metadataKey && isRequestSelected) {
      errorFieldNames.push(META_DATA);
    } else if ((!roles.length && !groups.length && !users.length && !others.length) && metadataKey && isRequestSelected) {
      errorFieldNames.push(`${errorPath}${ROLE_USER_GROUP}`);
    }
    return errorFieldNames;
  }

  @action
  setValidationError = (errorPath, rowData) => {
    if (rowData.metadataKey || (rowData.users?.length || rowData.groups?.length || rowData.roles?.length )) {
      this.errorListMap.has(errorPath) && this.errorListMap.delete(errorPath)
    }
  }

  setOptionsWithPrefix = (options, type, splitDelimiter) => {
    if (!options.slice().length) {
      return [];
    }
    return uniqBy(options.map(v => ({label: v, value: `${type}${splitDelimiter}${v}`})), 'value')
  }

  getPrefillUsersGroupsRolesValues = (field, splitDelimiter) => {
    const { users=[], groups=[], roles=[], others=[] } = field;
    return [
      ...this.setOptionsWithPrefix(users, 'users', splitDelimiter),
      ...this.setOptionsWithPrefix(groups, 'groups', splitDelimiter),
      ...this.setOptionsWithPrefix(roles, 'roles', splitDelimiter),
      ...this.setOptionsWithPrefix(others, 'others', splitDelimiter)
    ];
  }

  getFieldFormData = (fieldType="permissionRows") => {
    const formData = this.getFormData()
    return formData[fieldType];
  }
  setFormDataFieldValue = (fieldType="permissionRows", data) => {
    this.form.refresh({[fieldType]: data});
  }

  setUsersGroupsRolesChange = (value, errorPath) => {
    const { ROLE_USER_GROUP } = this.getPermissionErrorTypes();
    // const list = this.getFieldFormData();
    const obj = {
      users: [],
      groups: [],
      roles: [],
      others: []
    };
    if (value) {
      let pattern = /,(?=users##__##|groups##__##|roles##__##|others##__##)/;
      value.split(pattern).forEach(v => {
        const [type, val] = compact(v.split("##__##"));
        obj[type].push(val);
      });
      // select all will remove the other already selected.
      if (obj.others.length) {
        obj.users = [];
        obj.groups = [...obj.others];
        obj.roles = [];
        // delete obj.others;
      }
    }

    let data = this.getFormData();
    Object.assign(data, obj)
    // const rowData = cloneDeep(list[itemIndex]);
    this.form.refresh(data);
    this.setValidationError(`${errorPath}${ROLE_USER_GROUP}`, data);
  }

  setMetaDataChange = (value='') => {
    const { META_DATA } = this.getPermissionErrorTypes();
    const obj = this.getFormData();
    obj.metadataKey = value;

    this.form.refresh(obj);
    this.setValidationError(META_DATA, obj);
  }

  getPrefillMetaData = field => {
    const { metadataKey } = field;
    return uniq(metadataKey.slice()).map(v => ({label: v, value: v}));
  }

  resetForm = () => {
    this.clearErrorHashMap();
    this.restrictionMap.clear();
    this.form.clearForm();
  }

  getPermissionErrorTypes = () => {
    return ACCESS_PERMISSION_ERROR_TYPE;
  }
}

const ACCESS_PERMISSION_ERROR_TYPE = {
  META_DATA: "meta_data",
  ROLE_USER_GROUP: "role_user_group"
}


export default VectorDBPolicyFormUtil;