var applicationUtils = {};

  applicationUtils.processPermissionRows = (permissionRows, type) => {
    const access = permissionRows.filter(row => {
      if (type === 'allow') {
        return (
          row.prompt.allow === true &&
          row.reply.allow === true &&
          row.enrichedPrompt.allow === true
        );
      } else if (type === 'deny') {
        return (
          row.prompt.deny === true ||
          row.reply.deny === true ||
          row.enrichedPrompt.deny === true
        );
      }
      return false;
    });
  
    return access.reduce((acc, row) => {
      acc.users.push(...row.users);
      if (row.groups.includes('public')) {
        acc.users.push('Everyone');
      }
      acc.groups.push(...row.groups.filter(group => group !== 'public'));
      acc.roles.push(...row.roles);
      return acc;
    }, { users: [], groups: [], roles: [] });
  };

  applicationUtils.setPermissionRows = (models) => {
    const permissionsArray = [];
  
    models.forEach(model => {
      if (model.permissionRows && Array.isArray(model.permissionRows)) {
        permissionsArray.push(...model.permissionRows);
      }
    });
  
    return permissionsArray;
  };

  applicationUtils.setOptionsWithPrefix = (options, type, splitDelimiter) => {
    if (!options.slice().length) {
      return [];
    }
    return uniqBy(options.map(v => ({label: v, value: `${type}${splitDelimiter}${v}`})), 'value')
  }

  applicationUtils.getPrefillUsersGroupsRolesValues = (field, splitDelimiter) => {
    const { users=[], groups=[], roles=[], others=[] } = field;
    return [
      ...applicationUtils.setOptionsWithPrefix(users, 'users', splitDelimiter),
      ...applicationUtils.setOptionsWithPrefix(groups, 'groups', splitDelimiter),
      ...applicationUtils.setOptionsWithPrefix(roles, 'roles', splitDelimiter),
      ...applicationUtils.setOptionsWithPrefix(others, 'others', splitDelimiter)
    ];
  }

  export default applicationUtils;