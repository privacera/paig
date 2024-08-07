import React, {Fragment, Component} from 'react';
import {observer} from 'mobx-react';
import { compact } from 'lodash';

import {TableContainer, Table, TableHead, TableRow, TableBody,
    TableCell, Divider, Grid
} from '@material-ui/core';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import CloseIcon from '@material-ui/icons/Close';
import PersonIcon from '@material-ui/icons/Person';
import PeopleIcon from '@material-ui/icons/People';
import ContactsIcon from '@material-ui/icons/Contacts';

import { userGroupRolesLookups, metaDataLookUps, metaDataValueLookUps } from 'components/policies/field_lookups';
import {TagChip} from 'common-ui/lib/fs_select/fs_select';
import {Utils} from 'common-ui/utils/utils';
import {FormHorizontal, FormGroupInput, FormGroupSelect2, ValidationAsterisk} from 'common-ui/components/form_fields';
import { STATUS } from 'common-ui/utils/globals';

const TagValue = observer(({form, vectorDBPolicyFormUtil}) => {
    const {metadataKey, metadataValue} = form.fields;
    
    return (
        <Fragment>
            <TableCell className="permission-inputs">
                <div className="permission-metadata-value">
                    <FormGroupSelect2
                        required={true}
                        showLabel={false}
                        fieldObj={metadataKey}
                        variant="standard"
                        labelKey="label"
                        valueKey="label"
                        placeholder="Choose Vector DB Metadata"
                        triggerOnLoad={true}
                        forcePopupIcon={false}
                        data-testid="metadataKey"
                        className="permission-dropdown-fonts"
                        loadOptions={(searchString, callback) => {
                            metaDataLookUps(searchString, options => callback(options));
                        }}
                        onChange={(value) => {
                            metadataValue.value = ""
                            vectorDBPolicyFormUtil.setMetaDataChange(value)
                        }}
                        disableCloseOnSelect={true}
                    />
                </div>
            </TableCell>
            <TableCell className="permission-inputs"> 
                <div className="permission-metadata-value">
                    <FormGroupSelect2
                        value={metadataValue.value}
                        placeholder="Specify Values"
                        variant="standard"
                        labelKey="label"
                        valueKey="label"
                        triggerOnLoad={false}
                        loadOptionsOnOpen={true}
                        data-testid="metadataValue"
                        className="permission-dropdown-fonts"
                        allowCreate={true}
                        loadOptions={(searchString, callback) => {
                            if (metadataKey.value) {
                                metaDataValueLookUps(searchString, options => callback(options), undefined, {metadataName: metadataKey.value});
                            }
                        }}
                        onChange={value => metadataValue.value = value}
                        errMsg={metadataValue.errorMessage}
                    />
                </div>
            </TableCell>
        </Fragment>
    );
});

@observer
class GrantAccess extends Component {
    render() {
        const {form, vectorDBPolicyFormUtil} = this.props;

        const data = form.toJSON();
        const { ROLE_USER_GROUP } = vectorDBPolicyFormUtil.getPermissionErrorTypes();
        const splitDelimiter = "##__##";
        const userGroupRolesValue = vectorDBPolicyFormUtil.getPrefillUsersGroupsRolesValues({
            users: data.allowedUsers,
            groups: data.allowedGroups,
            roles: data.allowedRoles
        }, splitDelimiter);

        const errorListMap = vectorDBPolicyFormUtil.getErrorHashMap();
        const hasRoleUserGroupError = errorListMap.get(`allow${ROLE_USER_GROUP}`) === `allow${ROLE_USER_GROUP}`;

        return (
            <TableCell style={{position: "relative"}} className="permission-inputs grip-adjustment-cell">
                <FormGroupSelect2
                    error={hasRoleUserGroupError}
                    required={true}
                    showLabel={false}
                    value={userGroupRolesValue}
                    variant="standard"
                    allowCreate={false}
                    multiple={true}
                    labelKey="label"
                    valueKey="value"
                    placeholder="Grant Access to Users/Groups"
                    noOptionsText="Type to search Users and/or Groups"
                    triggerOnLoad={true}
                    forcePopupIcon={false}
                    data-testid="grant-access"
                    loadOptions={(searchString, callback) => {
                        this.infoOption = null;
                        userGroupRolesLookups(searchString, (options, op) => {
                            this.infoOption = op;
                            callback(options);
                        }, 'allowed');
                    }}
                    onChange={value => {
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
                        }
                        vectorDBPolicyFormUtil.setValidationError(`allow${ROLE_USER_GROUP}`, obj);

                        obj.allowedUsers = obj.users;
                        obj.allowedGroups = obj.groups;
                        obj.allowedRoles = obj.roles;
                        delete obj.users;
                        delete obj.groups;
                        delete obj.roles;

                        if (obj.others.length) {
                            obj.allowedUsers = [];
                            obj.allowedGroups = [...obj.others];
                            obj.allowedRoles = [];
                            delete obj.others;
                        }
                        if (obj.allowedGroups.includes('Everyone')) {
                            obj.deniedUsers = [];
                            obj.deniedGroups = [];
                            obj.deniedRoles = [];
                        } else if (obj.allowedUsers.length || obj.allowedGroups.length || obj.allowedRoles.length) {
                            obj.deniedGroups = data.deniedGroups.filter(g => g !== 'Everyone');
                            if (!obj.deniedGroups.includes('Others')) {
                                obj.deniedGroups.push('Others');
                            }
                        }
                        form.refresh(obj);
                    }}
                    disableCloseOnSelect={true}
                    renderTags={(tagValue, getTagProps) => (
                        tagValue.map((option, index) => {
                            const value = ''+option.value;
                            const [type, val] = compact(value.split(splitDelimiter));
                            const label = <div>{getIcon(type)} {val}</div>;
                            return (
                                <TagChip
                                    className="permission-labels"
                                    label={label}
                                    {...getTagProps({ index })}
                                    deleteIcon={<CloseIcon />}
                                />
                            )
                        })
                    )}
                    renderList={({options, listProps, listboxProps, getOptionProps, classes}) => {
                        let len = options.length;
                        return (
                            <Fragment>
                                <ul className={classes.listbox} {...listProps} {...listboxProps}>
                                    {
                                        options.map((option, index) => {
                                            const optionProps = getOptionProps({option, index});
                                            let disableClass = '';
                                            if (userGroupRolesValue.length &&  userGroupRolesValue[0]?.label === "Everyone") {
                                                disableClass = " inactive not-allowed ";
                                            }
                                            return (
                                                <li
                                                    {...optionProps}
                                                    className={`${classes.option}${disableClass}`}
                                                    style={{alignItems: 'normal'}}
                                                    key={option.model?.resource || index}
                                                >
                                                    <Grid item xs={9}>
                                                        <span className="opacity-40 m-r-sm font-12">
                                                            {option.type && getIcon(option.type.toLowerCase())}
                                                        </span>
                                                        <span>{option.label}</span>
                                                    </Grid>
                                                    <Grid item xs={3} className="opacity-40 font-12">
                                                        {option.type !== "OTHERS" && Utils.toTitleCase(option.type)}
                                                    </Grid>
                                                </li>
                                            )
                                        })
                                    }
                                </ul>
                                {
                                    this.infoOption &&
                                    <Fragment>
                                        <Divider />
                                        <li
                                            {...listProps}
                                            {...listboxProps}
                                            ref={null}
                                            className={classes.option}
                                            classes="disabled"
                                            aria-disabled="true"
                                            tabIndex="-1"
                                            style={{backgroundColor: '#eae9e9'}}
                                        >
                                            <Grid item xs={12} key="count">
                                                <Typography variant="caption" className="pull-right bold font-wt-500">
                                                    Showing Users: {this.infoOption.USERS}, Groups: {this.infoOption.GROUPS}
                                                </Typography>
                                            </Grid>
                                        </li>
                                    </Fragment>
                                }
                            </Fragment>
                        )
                    }}
                />
            </TableCell>
        );
    }
};

@observer
class DenyAccess extends Component {
    render() {
        const {form, vectorDBPolicyFormUtil} = this.props;
        const data = form.toJSON();
        const { ROLE_USER_GROUP } = vectorDBPolicyFormUtil.getPermissionErrorTypes();
        const splitDelimiter = "##__##";
        const userGroupRolesValue = vectorDBPolicyFormUtil.getPrefillUsersGroupsRolesValues({
            users: data.deniedUsers,
            groups: data.deniedGroups,
            roles: data.deniedRoles
        }, splitDelimiter);

        // const errorListMap = vectorDBPolicyFormUtil.getErrorHashMap();
        // const hasRoleUserGroupError = errorListMap.get(`deny${ROLE_USER_GROUP}`) === ROLE_USER_GROUP;

        return (
            <TableCell style={{position: "relative"}} className="permission-inputs grip-adjustment-cell">
                <FormGroupSelect2
                    //error={hasRoleUserGroupError}
                    required={false}
                    showLabel={false}
                    value={userGroupRolesValue}
                    variant="standard"
                    allowCreate={false}
                    multiple={true}
                    labelKey="label"
                    valueKey="value"
                    placeholder="Restrict Access for Users/Groups"
                    noOptionsText="Type to search Users and/or Groups"
                    triggerOnLoad={true}
                    forcePopupIcon={false}
                    data-testid="deny-access"
                    loadOptions={(searchString, callback) => {
                        this.infoOption = null;
                        userGroupRolesLookups(searchString, (options, op) => {
                            this.infoOption = op;
                            callback(options);
                        }, 'deny', 'Others');
                    }}
                    onChange={value => {
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
                        }
                        vectorDBPolicyFormUtil.setValidationError(`deny${ROLE_USER_GROUP}`, obj);

                        obj.deniedUsers = obj.users;
                        obj.deniedGroups = obj.groups;
                        obj.deniedRoles = obj.roles;
                        delete obj.users;
                        delete obj.groups;
                        delete obj.roles;

                        if (obj.others.length) {
                            obj.deniedGroups.push(...obj.others);
                            delete obj.others;
                        }
                        form.refresh(obj);
                    }}
                    disableCloseOnSelect={true}
                    renderTags={(tagValue, getTagProps) => (
                        tagValue.map((option, index) => {
                            const value = ''+option.value;
                            const [type, val] = compact(value.split(splitDelimiter));
                            const label = <div>{getIcon(type)} {val}</div>;
                            return (
                                <TagChip
                                    className="permission-labels"
                                    label={label}
                                    {...getTagProps({ index })}
                                    deleteIcon={<CloseIcon />}
                                />
                            )
                        })
                    )}
                    renderList={({options, listProps, listboxProps, getOptionProps, classes}) => {
                        let len = options.length;
                        return (
                            <Fragment>
                                <ul className={classes.listbox} {...listProps} {...listboxProps}>
                                    {
                                        options.map((option, index) => {
                                            const optionProps = getOptionProps({option, index});
                                            let disableClass = '';
                                            if (option.label === 'Others' && data.allowedGroups.includes('Everyone')) {
                                                disableClass = " inactive not-allowed ";
                                            }
                                            return (
                                            <li
                                                {...optionProps}
                                                className={`${classes.option}${disableClass}`}
                                                style={{alignItems: 'normal'}}
                                                key={option.model?.resource || index}
                                            >
                                                <Grid item xs={9}>
                                                    <span className="opacity-40 m-r-sm font-12">
                                                        {option.type && getIcon(option.type.toLowerCase())}
                                                    </span>
                                                    <span>{option.label}</span>
                                                </Grid>
                                                <Grid item xs={3} className="opacity-40 font-12">
                                                    {option.type !== "OTHERS" && Utils.toTitleCase(option.type)}
                                                </Grid>
                                            </li>
                                            )
                                        })
                                    }
                                </ul>
                                {
                                    this.infoOption &&
                                    <Fragment>
                                        <Divider />
                                        <li
                                            {...listProps}
                                            {...listboxProps}
                                            ref={null}
                                            className={classes.option}
                                            classes="disabled"
                                            aria-disabled="true"
                                            tabIndex="-1"
                                            style={{backgroundColor: '#eae9e9'}}
                                        >
                                            <Grid item xs={12} key="count">
                                                <Typography variant="caption" className="pull-right bold font-wt-500">
                                                    Showing Users: {this.infoOption.USERS}, Groups: {this.infoOption.GROUPS}
                                                </Typography>
                                            </Grid>
                                        </li>
                                    </Fragment>
                                }
                            </Fragment>
                        )
                    }}
                />
            </TableCell>
        );
    }
}

const VVectorDBPolicyForm = observer(({ form, vectorDBPolicyFormUtil }) => {
  const {name, description} = form.fields;

  return (
    <FormHorizontal alignItems="flex-start">
      <TableContainer>
        <Table className="permission-table-globals">
          <TableHead>
            <TableRow>
              {/* <TableCell className="restriction-desc" width="300px">Description <ValidationAsterisk /></TableCell> */}
                <TableCell className="restriction-tags" width="200px" data-testid="tag-cell">
                    <Tooltip
                        title={"This vector db metadata represents a specific category or type of data that you wish to apply filtering rules to."}
                        placement="top"
                        arrow
                    >
                        <span>
                            Vector DB Metadata
                            <ValidationAsterisk />
                        </span>
                    </Tooltip>
                </TableCell>
                <TableCell className="restriction-tags" width="200px" data-testid="tag-value-cell">
                    <Tooltip
                        title={"These values further define the data segments to which the filtering rules will be applied."}
                        placement="top"
                        arrow
                    >
                        <span>
                            Value
                            <ValidationAsterisk />
                        </span>
                    </Tooltip>
                </TableCell>
                <TableCell className="grip-adjustment-header restriction-users" width="300px" data-testid="granted-access-cell">
                    <Tooltip
                        title={"Select the users and groups who are authorized to access the data defined by the selected tag and values. Choosing 'Everyone' applies the rule to all users unless specific users or groups are also selected."}
                        placement="top"
                        arrow
                    >
                        <span>
                            Granted Access 
                            <ValidationAsterisk />
                        </span>
                    </Tooltip>
                </TableCell>
                <TableCell className="grip-adjustment-header restriction-users" width="300px" data-testid="denied-access-cell">
                    <Tooltip
                        title={"Identify users and groups who should be denied access to the data specified by the tag and its values. This restriction overrides any general access permissions."}
                        placement="top"
                        arrow
                    >
                        <span>
                            Denied Access
                        </span>
                    </Tooltip>
                </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow className="permission-row" data-testid="permission-row">
                {/* <TableCell>
                  <FormGroupInput
                    fieldObj={description}
                    onChange={e => {
                        name.value = e.target.value;
                        description.value = e.target.value;
                    }}
                    placeholder="Enter description"
                    variant="standard"
                    data-test="description"
                    className="permission-dropdown-fonts"
                  />
                </TableCell> */}
                <TagValue
                    form={form}
                    vectorDBPolicyFormUtil={vectorDBPolicyFormUtil}
                    data-testid="tag-value-row"
                />
                <GrantAccess
                    form={form}
                    vectorDBPolicyFormUtil={vectorDBPolicyFormUtil}
                    data-testid="granted-access-row"
                />
                <DenyAccess
                    form={form}
                    vectorDBPolicyFormUtil={vectorDBPolicyFormUtil}
                    data-testid="denied-access-row"
                />
              </TableRow>
            </TableBody>
        </Table>
      </TableContainer>
    </FormHorizontal>
  );
})

const getIcon = type => {
  const common = { fontSize: "small" }
  switch(type) {
    case 'users':
      return <PersonIcon {...common} />;
    case "groups":
      return <PeopleIcon {...common} />
    case "roles":
      return <ContactsIcon {...common} />
    case "others":
      return <PeopleIcon {...common} />
  }
}

const vector_db_policy_form_def = {
  id: {},
  name: {},
  description: {
    defaultValue: "",
    // validators: {
    //   errorMessage: 'Required!',
    //   fn: (field) => {
    //     return Utils.characterValidation(field);
    //   }
    // }
  },
  status: {
    defaultValue: STATUS.enabled.value
  },
  allowedUsers: {
    defaultValue: []
  },
  allowedGroups: {
    defaultValue: []
  },
  allowedRoles: {
    defaultValue: []
  },
  deniedUsers: {
    defaultValue: []
  },
  deniedGroups: {
    defaultValue: []
  },
  deniedRoles: {
    defaultValue: []
  },
  metadataKey: {
    defaultValue: '',
    validators: {
      errorMessage: 'Required!',
      fn: (field) => {
        return field.value.length > 0;
      }
    }
  },
  metadataValue: {
    defaultValue: '',
    validators: {
      errorMessage: 'Required!',
      fn: (field) => {
        return field.value.trim().length > 0;
      }
    }
  },
  operator: {
    defaultValue: 'eq'
  },
  vectorDBId: {}
}

export default VVectorDBPolicyForm;
export {
  vector_db_policy_form_def
}