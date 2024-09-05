import { isEmpty, uniqBy, compact, uniq } from "lodash";
import { observable, action, ObservableMap } from "mobx";
import { PROMPT_REPLY_TYPE } from 'utils/globals';

class AIPolicyFormUtil {
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

    if (payload.groups[0] === 'public') {
      // payload.others = [];
      payload.groups = ['Everyone'];
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
    const { PERMISSIONS } = this.getPermissionErrorTypes();

    const formData = this.getFormData()
    
    const fieldNames = this.getPermissionErrorFieldKeys(formData);
    if (!isEmpty(fieldNames)) {
      if (Array.isArray(fieldNames)) {
        fieldNames.forEach(name => {
          this.errorListMap.set(`${PERMISSIONS}${name}`, name);
        })
      } else {
        this.errorListMap.set(`${PERMISSIONS}${fieldNames}`, fieldNames);
      }
    }

    return !this.errorListMap.size;
  }

  getPermissionErrorFieldKeys = (field) => {
    const { ROLE_USER_GROUP, SENSITIVE_DATA, REQUEST_TYPE } = this.getPermissionErrorTypes();
    const { roles=[], groups=[], users=[], others=[], tags=[] } = field;
    const errorFieldNames = [];
    const isRequestSelected = true; //this.checkTypeAndActionValue(field);
    if ((!roles.length && !groups.length && !users.length && !others.length) && !tags.length && !isRequestSelected) {
      errorFieldNames.push(...[ROLE_USER_GROUP, SENSITIVE_DATA, REQUEST_TYPE]);
    } else if ((roles.length || groups.length || users.length || others.length) && !tags.length && !isRequestSelected) {
      errorFieldNames.push(...[SENSITIVE_DATA, REQUEST_TYPE]);
    } else if ((!roles.length && !groups.length && !users.length && !others.length) && tags.length && !isRequestSelected) {
      errorFieldNames.push(...[ROLE_USER_GROUP, REQUEST_TYPE]);
    } else if ((!roles.length && !groups.length && !users.length && !others.length) && !tags.length && isRequestSelected) {
      errorFieldNames.push(...[ROLE_USER_GROUP, SENSITIVE_DATA]);
    } else if ((roles.length || groups.length || users.length || others.length) && !tags.length && isRequestSelected) {
      errorFieldNames.push(SENSITIVE_DATA);
    } else if ((!roles.length && !groups.length && !users.length && !others.length) && tags.length && isRequestSelected) {
      errorFieldNames.push(ROLE_USER_GROUP);
    } else if ((roles.length || groups.length || users.length || others.length) && tags.length && !isRequestSelected) {
      errorFieldNames.push(REQUEST_TYPE);
    }
    return errorFieldNames;
  }

  @action
  setValidationError = (errorPath, rowData) => {
    if (rowData.tags?.length || /*this.checkTypeAndActionValue(rowData) ||*/  (rowData.users?.length || rowData.groups?.length || rowData.roles?.length )) {
      this.errorListMap.has(errorPath) && this.errorListMap.delete(errorPath)
    }
  }

  arrangeDownToUP = (dragIndex, draggedIndex) => {
    const { PERMISSIONS } = this.getPermissionErrorTypes();
    const downPath = `${PERMISSIONS}${dragIndex}`;
    const downHasRestrict = this.restrictionMap.has(downPath);

    for(let i=dragIndex; i>draggedIndex; i--) {
      const restrictPath = `${PERMISSIONS}${(i-1)}`;
      if (this.restrictionMap.has(restrictPath)) {
        this.restrictionMap.delete(restrictPath);
        this.restrictionMap.set(`${PERMISSIONS}${i}`, true);
      }
    }
    if (downHasRestrict) {
      this.restrictionMap.delete(`${PERMISSIONS}${dragIndex}`);
      this.restrictionMap.set(`${PERMISSIONS}${draggedIndex}`, true);
    }
  }

  arrangeUpToDown = (dragIndex, draggedIndex) => {
    const { PERMISSIONS } = this.getPermissionErrorTypes();
    const upPath = `${PERMISSIONS}${dragIndex}`;
    const upHasRestrict = this.restrictionMap.has(upPath);

    for(let i=dragIndex; i<draggedIndex; i++) {
      const restrictPath = `${PERMISSIONS}${(i+1)}`;
      if (this.restrictionMap.has(restrictPath)) {
        this.restrictionMap.delete(restrictPath);
        this.restrictionMap.set(`${PERMISSIONS}${i}`, true);
      }
    }
    if (upHasRestrict) {
      this.restrictionMap.delete(`${PERMISSIONS}${dragIndex}`);
      this.restrictionMap.set(`${PERMISSIONS}${draggedIndex}`, true);
    }
  }

  reArrangeRestrictionAfterDrag = (dragIndex, draggedIndex) => {
    if (dragIndex > draggedIndex) {
      this.arrangeDownToUP(dragIndex, draggedIndex)
    } else {
      this.arrangeUpToDown(dragIndex, draggedIndex);
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

  setUsersGroupsRolesChange = (value, itemIndex) => {
    const { ROLE_USER_GROUP, PERMISSIONS } = this.getPermissionErrorTypes();
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
    this.setValidationError(`${PERMISSIONS}${ROLE_USER_GROUP}`, data);
  }

  setSensitiveDataChange = (value='', itemIndex) => {
    const { SENSITIVE_DATA, PERMISSIONS } = this.getPermissionErrorTypes();
    const obj = this.getFormData();
    obj.tags = compact(value.split(','))

    this.form.refresh(obj);
    this.setValidationError(`${PERMISSIONS}${SENSITIVE_DATA}`, obj);
  }

  getPrefillSensitiveData = field => {
    const { tags } = field;
    return uniq(tags.slice()).map(v => ({label: v, value: v}));
  }

  resetForm = () => {
    this.clearErrorHashMap();
    this.restrictionMap.clear();
    this.form.clearForm();
  }

  getBooleanValueObj = (field, keyName, value) => {
    const keys = Object.keys(field);
    keys.forEach(k => {
      field[k] = k === keyName ? value : false;
    })
    return field;
  }

  promptReplyChange = (value, fieldType, attrName, itemIndex) => {
    const { REQUEST_TYPE, PERMISSIONS } = this.getPermissionErrorTypes();
    const formData = this.getFormData();
    let obj =  this.updatePromptReplyValues(value, fieldType, attrName, obj, false);
    this.setValidationError(`${PERMISSIONS}${REQUEST_TYPE}`, rowData);
  }

  updatePromptReplyValues = (value, fieldType, attrName, obj, autoSelectField=true) => {
    obj[fieldType] = this.getBooleanValueObj(obj[fieldType], attrName, value);
    // The requirement will change in future, But now auto selecting the same attrName from other 'prompt', 'reply'
    if (autoSelectField) {
      const autoSelectFieldName = fieldType === PROMPT_REPLY_TYPE.PROMPT ? PROMPT_REPLY_TYPE.REPLY : PROMPT_REPLY_TYPE.PROMPT;
      obj[autoSelectFieldName] = this.getBooleanValueObj(obj[autoSelectFieldName], attrName, value);
      obj[PROMPT_REPLY_TYPE.ENRICH_PROMPT] = this.getBooleanValueObj(obj[PROMPT_REPLY_TYPE.ENRICH_PROMPT], attrName, value);
    }
    return obj;
  }
  getPermissionErrorTypes = () => {
    return ACCESS_PERMISSION_ERROR_TYPE;
  }

  resetActionRequest = (attrName, value, itemIndex) => {
    const { PERMISSIONS, REQUEST_TYPE } = this.getPermissionErrorTypes();
    const list = this.getFieldFormData();
    const fieldType = PROMPT_REPLY_TYPE.PROMPT;
    const errorPath = `${PERMISSIONS}${REQUEST_TYPE}`;
    this.promptReplyChange(false, fieldType, attrName, itemIndex);
    this.errorListMap.delete(errorPath);
    let obj =  this.updatePromptReplyValues(value, fieldType, attrName, list[itemIndex], true);
    list[itemIndex] = obj;
    this.setFormDataFieldValue(list);
  }

}

const ACCESS_PERMISSION_ERROR_TYPE = {
  PERMISSIONS: 'permissionRows',
  SENSITIVE_DATA: "sensitive_data",
  ROLE_USER_GROUP: "role_user_group",
  REQUEST_TYPE: "request_type"
}


export default AIPolicyFormUtil;