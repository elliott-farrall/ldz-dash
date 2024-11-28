# Function to display the welcome menu
display_menu() {
    echo "  _      _____ ______"
    echo " | |    |  __ \___  /"
    echo " | |    | |  | | / / "
    echo " | |    | |  | |/ /  "
    echo " | |____| |__| / /__ "
    echo " |______|_____/_____|"
    echo "                     "
    echo "                     "
    echo
    echo "Welcome to the LDZ Data Migration Tool"
    echo
    echo "Please select a mode:"
    echo "1) Rename a column heading"
    echo "2) Rename all instances of a row value"
    echo "3) Remove a column"
    echo "4) Exit"
    echo
}

# Function to list categories
list_categories() {
    find "$DATA_DIR" -mindepth 2 -maxdepth 2 -type d -exec basename {} \; | sort | uniq
}

# Function to list subcategories
list_subcategories() {
    local category=$1
    find "$DATA_DIR" -mindepth 3 -maxdepth 3 -type f -path "*/$category/*.csv" -exec basename {} .csv \; | sort | uniq
}

# Function to prompt user for input
prompt_user() {
    local prompt=$1
    local options=("${!2}")
    echo "$prompt" >&2
    select opt in "${options[@]}"; do
        if [[ -n $opt ]]; then
            echo "$opt"
            return
        else
            echo "Invalid option. Please try again." >&2
        fi
    done
}

# Function to create a backup of the entire DATA_DIR with only CSV files
create_backup() {
    local backup_name="backup_$(date +'%Y%m%d_%H%M%S').zip"
    (cd "$DATA_DIR" && find . -type f -name "*.csv" -print | zip -q "$backup_name" -@)
    echo "Backup of CSV files in the data directory created at $DATA_DIR/$backup_name"
}

# Function to update column name
update_column_name() {
    local file=$1
    local old_value=$2
    local new_value=$3
    awk -v old="$old_value" -v new="$new_value" '
    BEGIN { FS=OFS="," }
    NR==1 {
        for (i=1; i<=NF; i++) {
            if ($i == old) {
                $i = new
            }
        }
    }
    { print }
    ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
}

# Function to update row values
update_row_values() {
    local file=$1
    local column_name=$2
    local old_value=$3
    local new_value=$4
    awk -v col="$column_name" -v old="$old_value" -v new="$new_value" '
    BEGIN { FS=OFS="," }
    NR==1 {
        for (i=1; i<=NF; i++) {
            if ($i == col) {
                colnum = i
            }
        }
    }
    {
        if (NR > 1 && $colnum == old) {
            $colnum = new
        }
        print
    }
    ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
}

# Function to remove a column
remove_column() {
    local file=$1
    local column_name=$2
    awk -v col="$column_name" '
    BEGIN { FS=OFS="," }
    NR==1 {
        for (i=1; i<=NF; i++) {
            if ($i == col) {
                colnum = i
            }
        }
    }
    {
        for (i=1; i<=NF; i++) {
            if (i != colnum) {
                printf "%s%s", $i, (i==NF ? ORS : OFS)
            }
        }
    }
    ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
}

# Main script
DATA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Display the welcome menu and prompt user for mode
while true; do
    display_menu
    read -p "Enter your choice [1-4]: " choice
    case $choice in
        1)
            MODE="rename_column"
            break
            ;;
        2)
            MODE="rename_row"
            break
            ;;
        3)
            MODE="remove_column"
            break
            ;;
        4)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid choice. Please select a valid option."
            ;;
    esac
done

# Prompt user for category
categories=($(list_categories))
CATEGORY=$(prompt_user "Select a category:" categories[@])

# Prompt user for subcategory
subcategories=($(list_subcategories "$CATEGORY"))
SUBCATEGORY=$(prompt_user "Select a subcategory:" subcategories[@])

# Prompt user for column name
read -p "Enter the column name: " COLUMN_NAME

if [ "$MODE" == "rename_column" ]; then
    # Prompt user for old and new column names
    OLD_VALUE=$COLUMN_NAME
    read -p "Enter the new column name: " NEW_VALUE
elif [ "$MODE" == "rename_row" ]; then
    # Prompt user for old and new row values
    read -p "Enter the old row value: " OLD_VALUE
    read -p "Enter the new row value: " NEW_VALUE
elif [ "$MODE" == "remove_column" ]; then
    # No additional input needed for remove column mode
    OLD_VALUE=$COLUMN_NAME
fi

# Create a backup of the entire DATA_DIR with only CSV files
echo
create_backup

# Find all relevant CSV files
find "$DATA_DIR" -type f -path "*/$CATEGORY/$SUBCATEGORY.csv" | while read -r FILE; do
    RELATIVE_FILE=$(realpath --relative-to="$DATA_DIR" "$FILE")
    if [ "$MODE" == "rename_column" ]; then
        update_column_name "$FILE" "$OLD_VALUE" "$NEW_VALUE"
        echo "Updated column name from $OLD_VALUE to $NEW_VALUE in $RELATIVE_FILE"
    elif [ "$MODE" == "rename_row" ]; then
        update_row_values "$FILE" "$COLUMN_NAME" "$OLD_VALUE" "$NEW_VALUE"
        echo "Updated row values from $OLD_VALUE to $NEW_VALUE in column $COLUMN_NAME in $RELATIVE_FILE"
    elif [ "$MODE" == "remove_column" ]; then
        remove_column "$FILE" "$OLD_VALUE"
        echo "Removed column $OLD_VALUE in $RELATIVE_FILE"
    fi
done
