#!/bin/bash
set -e
if [ $# -lt 1 ]; then
  echo "Usage: sh $0 <branch-name>"
  exit 1
fi
BRANCH_NAME=$1

S3_BUCKET=$S3_BUCKET
S3_BASE_PATH=s3://${S3_BUCKET}/stage
S3_PATH=${S3_BASE_PATH}/$BRANCH_NAME
LOCAL_PATH=mkdocs/site

AWS_ACCOUNT=$AWS_ACCOUNT
AWS_ASSUME_ROLE=$AWS_ASSUME_ROLE
# shellcheck disable=SC2164
cd "$(dirname $0)"
set -x
./mkdocs/run_paig_mkdocs_docker.sh build
aws s3 cp --recursive $LOCAL_PATH "$S3_PATH"

#Unset set -e
set +e

# Write a function to delete non-existing branches from S3
pruneS3BranchFolders() {
  echo "Checking to see if any branches have been deleted from git and need to be deleted from S3."
    local s3_bucket="$1"

    if [[ -z "$s3_bucket" ]]; then
        echo "Please provide an S3 bucket name."
        return 1
    fi

    # 1. Get the branches in the git repo
    git fetch origin
    local local_branches=$(git branch -r | sed 's/ *origin\///' | sed '/->/d')

    # 2. List the folders in S3 under s3://$s3_bucket/stage/
    local s3_folders=$(aws s3 ls ${S3_BASE_PATH}/ | grep -Eo '[^ ]+/$' | sed 's|/$||')

    # 3. Compare and delete non-existing branches from S3
    for folder in $s3_folders; do
        echo "Checking if branch $folder exists in git ..."
        local exists=0
        for branch in $local_branches; do
            if [[ $folder == $branch ]]; then
                exists=1
                break
            fi
        done

        if [[ $exists -eq 0 ]]; then
            echo "$folder is deleted, so deleting ${S3_BASE_PATH}/$folder/"
            #aws s3 rm ${S3_BASE_PATH}/$folder/ --recursive
        fi
    done
}

pruneS3BranchFolders $S3_BUCKET

generateHTMLTable() {
    git fetch origin
    branches=$(git branch -r | sed 's/ *origin\///' | sed '/->/d')

    # Start the table with added styles
    echo '<!DOCTYPE html>'
    echo '<html lang="en">'
    echo '<head>'
    echo '    <meta charset="UTF-8">'
    echo '    <title>Document Branches</title>'

cat <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Document Branches</title>
<style>
table { width: 100%; border-collapse: collapse; margin: 20px 0; }
th, td { border: 1px solid #ddd; padding: 8px 12px; }
th { background-color: #f2f2f2; }
tr:hover { background-color: #f5f5f5; }
</style>
</head>
EOF

cat <<EOF
<body>
<h2>Document Branches</h2>
<table>
<thead><tr><th>Branch</th><th>Last Commit Message</th><th>Committer</th><th>Relative Time</th><th>Commit Time (PT)</th><th>Commit Time (IST)</th></tr></thead>
<tbody>
EOF

    for branch in $branches; do
        last_commit_msg=$(git log origin/$branch -n 1 --pretty=format:"%s")
        committer_name=$(git log origin/$branch -n 1 --pretty=format:"%cn")
        relative_time=$(git log origin/$branch -n 1 --pretty=format:"%cd" --date=relative)
        commit_time_pt=$(TZ=America/Los_Angeles git log origin/$branch -n 1 --pretty=format:"%cd" --date=format-local:"%Y-%m-%d %H:%M:%S")
        commit_time_ist=$(TZ=Asia/Kolkata git log origin/$branch -n 1 --pretty=format:"%cd" --date=format-local:"%Y-%m-%d %H:%M:%S")
        commit_time_utc=$(git log origin/$branch -n 1 --pretty=format:"%cd" --date=format-local:"%Y-%m-%dT%H:%M:%S" --date=utc)
        commit_time_utc=$(git log origin/$branch -n 1 --pretty=format:"%cd" --date=iso-strict)

        # Print the row for this branch with added hyperlink
        echo "<tr><td><a href=\"./$branch/index.html\">$branch</a></td><td>$last_commit_msg</td><td>$committer_name</td><td data-time=\"$commit_time_utc\">loading...</td><td>$commit_time_pt</td><td>$commit_time_ist</td></tr>"
    done

cat <<EOF
</tbody>
</table>
<script>
function timeDifference(current, previous) {
    const msPerMinute = 60 * 1000;
    const msPerHour = msPerMinute * 60;
    const msPerDay = msPerHour * 24;
    const msPerMonth = msPerDay * 30;
    const msPerYear = msPerDay * 365;
    const elapsed = current - previous;

    if (elapsed < msPerMinute) {
        return Math.round(elapsed/1000) + ' seconds ago';
    } else if (elapsed < msPerHour) {
        return Math.round(elapsed/msPerMinute) + ' minutes ago';
    } else if (elapsed < msPerDay ) {
        return Math.round(elapsed/msPerHour ) + ' hours ago';
    } else if (elapsed < msPerMonth) {
        return Math.round(elapsed/msPerDay) + ' days ago';
    } else if (elapsed < msPerYear) {
        return Math.round(elapsed/msPerMonth) + ' months ago';
    } else {
        return Math.round(elapsed/msPerYear ) + ' years ago';
    }
}

document.querySelectorAll('[data-time]').forEach(function(element) {
    const timeString = element.getAttribute('data-time');
    const timeDate = new Date(timeString);
    element.textContent = timeDifference(new Date(), timeDate);
});
</script>
</body>
</html>
EOF

}


generateHTMLTable > index.html

destination_path="${S3_BASE_PATH}/index.html"
aws s3 cp index.html $destination_path --content-type "text/html" --content-disposition "inline; filename=index.html"

# Optionally delete the index.html file from local after uploading
# rm index.html

DOCS_STAGE_LOCATION="https://$S3_BUCKET.s3.amazonaws.com/stage/index.html"
if [ "$BRANCH_NAME" == "main" ]; then
    # Assume the role and get temporary credentials
  TEMP_ROLE=$(aws sts assume-role --role-arn "arn:aws:iam::$AWS_ACCOUNT:role/$AWS_ASSUME_ROLE" --role-session-name "AssumedRoleSession")
  
  # Export the temporary credentials
  export AWS_ACCESS_KEY_ID=$(echo $TEMP_ROLE | jq -r '.Credentials.AccessKeyId')
  export AWS_SECRET_ACCESS_KEY=$(echo $TEMP_ROLE | jq -r '.Credentials.SecretAccessKey')
  export AWS_SESSION_TOKEN=$(echo $TEMP_ROLE | jq -r '.Credentials.SessionToken')

  aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DISTRIBUTION_ID --paths '/*'
fi

echo "Docs have been deployed to:"
echo "$DOCS_STAGE_LOCATION"
