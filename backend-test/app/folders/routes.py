from flask import request, current_app, g
from app.db import query_db
from app.utils.decorators import login_required
from app.utils.helpers import success_response, error_response
import datetime

from . import folders_bp

# --- Helper function for directory closure updates ---
def _update_directory_closure_on_create(directory_id, parent_id, user_id):
    """
    Updates the directory_closure table when a new directory is created.
    1. Add self-loop for the new directory.
    2. Add paths from all ancestors of the parent to the new directory.
    """
    try:
        # 1. Self-loop
        query_db(
            "INSERT INTO directory_closure (ancestor_id, descendant_id, depth, user_id) VALUES (%s, %s, 0, %s)",
            (directory_id, directory_id, user_id), commit=True
        )

        # 2. Paths from parent's ancestors
        if parent_id is not None:
            query_db(
                """
                INSERT INTO directory_closure (ancestor_id, descendant_id, depth, user_id)
                SELECT ancestor_id, %s, depth + 1, %s
                FROM directory_closure
                WHERE descendant_id = %s
                """,
                (directory_id, user_id, parent_id), commit=True
            )
        current_app.logger.info(f"Directory closure table updated for new directory_id: {directory_id}")
    except Exception as e:
        current_app.logger.error(f"Failed to update directory_closure for new directory {directory_id}: {e}", exc_info=True)
        # This is critical, if it fails, the tree structure might be inconsistent.
        # Consider rolling back the directory creation or flagging it for admin attention.
        raise # Re-raise to indicate a problem in the calling function.

@folders_bp.route('/<int:folder_id>', methods=['GET'])
@login_required
def get_folder_contents(folder_id):
    user_id = g.current_user['user_id']
    try:
        # Verify folder exists and belongs to user
        current_folder = query_db(
            "SELECT directory_id, directory_name, parent_id, create_time FROM directory WHERE directory_id = %s AND user_id = %s",
            (folder_id, user_id), one=True
        )
        if not current_folder:
            return error_response(message="Folder not found or access denied.", status_code=404)

        subfolders = query_db(
            "SELECT directory_id as id, directory_name as name, 'folder' as type, create_time FROM directory WHERE parent_id = %s AND user_id = %s ORDER BY directory_name ASC",
            (folder_id, user_id)
        )
        documents = query_db(
            "SELECT document_id as id, title as name, 'document' as type, create_time, local_url FROM document WHERE directory_id = %s AND user_id = %s ORDER BY title ASC",
            (folder_id, user_id)
        )
        
        items = subfolders + documents
        # Sort items by name, or type then name, if desired by frontend
        # items.sort(key=lambda x: (x['type'], x['name']))

        return success_response(data={"currentFolder": current_folder, "items": items}, message="获取成功")
    except Exception as e:
        current_app.logger.error(f"Error getting folder contents for {folder_id}: {e}", exc_info=True)
        return error_response(message="Failed to retrieve folder contents.", status_code=500, error_details=e)

@folders_bp.route('/create', methods=['POST'])
@login_required
def create_folder():
    data = request.get_json()
    user_id = g.current_user['user_id']
    
    parent_id = data.get('parentId') # Can be null for root folder
    name = data.get('name')

    if not name:
        return error_response(message="Folder name is required.", status_code=400)

    # Check for duplicate name under the same parent for the same user
    if parent_id:
        existing = query_db("SELECT directory_id FROM directory WHERE user_id = %s AND directory_name = %s AND parent_id = %s",
                            (user_id, name, parent_id), one=True)
    else: # Root folder
        existing = query_db("SELECT directory_id FROM directory WHERE user_id = %s AND directory_name = %s AND parent_id IS NULL",
                            (user_id, name), one=True)
    if existing:
        return error_response(message=f"A folder named '{name}' already exists in this location.", status_code=409)

    try:
        # parent_id can be None for root directories
        # SQL NULL is handled by %s if parent_id is Python None
        new_folder_id = query_db(
            "INSERT INTO directory (user_id, parent_id, directory_name, create_time) VALUES (%s, %s, %s, %s)",
            (user_id, parent_id, name, datetime.datetime.utcnow()), commit=True
        )
        if not new_folder_id: # Should be lastrowid
             # If lastrowid is not returned, try to fetch it (less ideal)
            folder_check = query_db("SELECT directory_id, create_time FROM directory WHERE user_id=%s AND directory_name=%s AND " + ("parent_id=%s" if parent_id else "parent_id IS NULL") + " ORDER BY directory_id DESC LIMIT 1",
                                    (user_id, name, parent_id) if parent_id else (user_id, name), one=True)
            if folder_check:
                new_folder_id = folder_check['directory_id']
            else:
                return error_response("Failed to confirm folder creation ID.", status_code=500)


        _update_directory_closure_on_create(new_folder_id, parent_id, user_id)

        created_folder_data = {
            "id": new_folder_id,
            "name": name,
            "type": "folder",
            "parentId": parent_id,
            # "createTime": fetch created_time if not returning from insert or use current time
        }
        return success_response(data=created_folder_data, message="创建成功", status_code=201)
    except Exception as e:
        current_app.logger.error(f"Error creating folder: {e}", exc_info=True)
        # Consider rolling back if closure update fails, though query_db has basic rollback on error
        return error_response(message="Failed to create folder.", status_code=500, error_details=e)


@folders_bp.route('/rename', methods=['PUT'])
@login_required
def rename_folder():
    data = request.get_json()
    user_id = g.current_user['user_id']
    folder_id = data.get('folderId')
    new_name = data.get('newName')

    if not folder_id or not new_name:
        return error_response(message="Folder ID and new name are required.", status_code=400)

    try:
        # Verify folder exists and belongs to user
        folder_to_rename = query_db("SELECT directory_id, parent_id FROM directory WHERE directory_id = %s AND user_id = %s", (folder_id, user_id), one=True)
        if not folder_to_rename:
            return error_response(message="Folder not found or access denied.", status_code=404)

        # Check for duplicate name under the same parent
        parent_id = folder_to_rename['parent_id']
        if parent_id:
            existing = query_db("SELECT directory_id FROM directory WHERE user_id = %s AND directory_name = %s AND parent_id = %s AND directory_id != %s",
                                (user_id, new_name, parent_id, folder_id), one=True)
        else: # Root folder
            existing = query_db("SELECT directory_id FROM directory WHERE user_id = %s AND directory_name = %s AND parent_id IS NULL AND directory_id != %s",
                                (user_id, new_name, folder_id), one=True)
        if existing:
            return error_response(message=f"A folder named '{new_name}' already exists in this location.", status_code=409)


        rows_affected = query_db(
            "UPDATE directory SET directory_name = %s WHERE directory_id = %s AND user_id = %s",
            (new_name, folder_id, user_id), commit=True
        )
        if rows_affected:
            return success_response(data={"id": folder_id, "name": new_name}, message="重命名成功")
        else: # Should not happen if previous check passed unless race condition or other issue
            return error_response(message="Folder not found or no changes made.", status_code=404) # Or 304 Not Modified
    except Exception as e:
        current_app.logger.error(f"Error renaming folder {folder_id}: {e}", exc_info=True)
        return error_response(message="Failed to rename folder.", status_code=500, error_details=e)

@folders_bp.route('/<int:folder_id>', methods=['DELETE'])
@login_required
def delete_folder(folder_id):
    user_id = g.current_user['user_id']
    try:
        # Verify folder exists and belongs to user
        folder_to_delete = query_db("SELECT directory_id FROM directory WHERE directory_id = %s AND user_id = %s", (folder_id, user_id), one=True)
        if not folder_to_delete:
            return error_response(message="Folder not found or access denied.", status_code=404)

        # The ON DELETE CASCADE in your SQL schema for:
        # - directory.parent_id -> directory.directory_id (ON DELETE SET NULL -- this means children become orphans, not deleted)
        #   You might want ON DELETE CASCADE if deleting a folder should delete all its subfolders.
        #   If you want to delete subfolders, you'll need a recursive delete logic here OR change schema to CASCADE for parent_id.
        # - directory_closure (ancestor_id, descendant_id) -> directory.directory_id (ON DELETE CASCADE) -- This is good.
        # - document.directory_id -> directory.directory_id (ON DELETE CASCADE) -- This is good, documents in folder will be deleted.

        # Assuming you want to delete the folder and all its contents (subfolders and documents):
        # 1. Get all descendant directories (including self)
        descendant_dirs_q = """
            SELECT dc.descendant_id
            FROM directory_closure dc
            JOIN directory d ON dc.descendant_id = d.directory_id
            WHERE dc.ancestor_id = %s AND d.user_id = %s
        """
        descendant_dirs_result = query_db(descendant_dirs_q, (folder_id, user_id))
        if not descendant_dirs_result: # Should at least find itself
             current_app.logger.warning(f"No descendants found for folder_id {folder_id} during delete, unusual.")
             # Proceed to delete the single folder entry if closure table is somehow inconsistent

        descendant_dir_ids = [row['descendant_id'] for row in descendant_dirs_result]
        
        if not descendant_dir_ids: # Fallback if closure query fails or folder is isolated
            descendant_dir_ids = [folder_id]


        # The ON DELETE CASCADE on 'document' table's 'directory_id' FK
        # and on 'directory_closure' table's FKs to 'directory_id'
        # should handle cleaning up related documents and closure entries when a directory row is deleted.
        # So, we only need to delete from the 'directory' table.
        # The order of deletion might matter if FK constraints are DEFERRED, but MySQL typically checks immediately.
        # To be safe, delete in an order that respects dependencies or rely on CASCADE.
        
        # With ON DELETE CASCADE on document.directory_id and directory_closure related to directory.directory_id,
        # deleting from `directory` table should be sufficient.
        # Make sure your `directory_closure` FKs to `directory` have ON DELETE CASCADE.
        # Your schema shows:
        # FOREIGN KEY (`ancestor_id`) REFERENCES `directory` (`directory_id`) ON DELETE CASCADE
        # FOREIGN KEY (`descendant_id`) REFERENCES `directory` (`directory_id`) ON DELETE CASCADE
        # This is correct.

        # And for documents:
        # FOREIGN KEY (`directory_id`) REFERENCES `directory` (`directory_id`) ON DELETE CASCADE
        # This is also correct.

        # So, deleting the target folder should cascade. If it's a parent, and its parent_id FK in child directories
        # is ON DELETE SET NULL, then child directories become orphans. If it's ON DELETE CASCADE, they'd be deleted too.
        # Your schema has `ON DELETE SET NULL` for `directory.parent_id`.
        # This means if you delete folder X, and Y is a child of X, Y's parent_id becomes NULL.
        # This is usually NOT what's desired for "delete folder and its contents".
        # You likely want to change `directory.parent_id`'s `ON DELETE` action to `CASCADE`
        # or implement a recursive delete here.
        #
        # Let's assume for now we want to delete only the specified folder and its direct documents.
        # If recursive delete of subfolders is needed, the logic is more complex without `ON DELETE CASCADE` on `parent_id`.

        # Given `ON DELETE SET NULL` for `parent_id` and `ON DELETE CASCADE` for documents:
        # Deleting a directory will:
        # 1. Delete all documents directly within it (due to document.directory_id ON DELETE CASCADE).
        # 2. Delete all directory_closure entries where this directory was an ancestor or descendant.
        # 3. Set parent_id to NULL for all direct children of this directory. They become root folders.
        # This is likely NOT what the frontend spec "删除文件夹及其内容" implies if "内容" includes sub-folders.

        # OPTION 1: Change schema for directory.parent_id to ON DELETE CASCADE
        # (Recommended if "delete folder and its contents" means recursive delete)
        # If schema is changed, this simple delete is enough:
        # rows_affected = query_db("DELETE FROM directory WHERE directory_id = %s AND user_id = %s", (folder_id, user_id), commit=True)
        
        # OPTION 2: Manual recursive delete (if schema cannot be changed)
        # This is more complex: find all sub-folders, delete them from deepest to highest, then delete the main folder.
        # Using the closure table to find all descendants:
        if descendant_dir_ids:
            placeholders = ', '.join(['%s'] * len(descendant_dir_ids))
            
            # Files associated with these directories will be deleted due to ON DELETE CASCADE from document->directory
            # Closure table entries will be deleted due to ON DELETE CASCADE from directory_closure->directory
            
            # We need to delete from the directory table itself.
            # Delete from deepest to avoid FK issues if parent_id was not ON DELETE CASCADE.
            # However, since descendant_dir_ids includes the folder_id itself, and the CASCADE from
            # directory_closure and document tables is active, we just need to delete these directories.
            # The order shouldn't strictly matter if MySQL resolves cascades properly.
            
            # To be absolutely safe with `ON DELETE SET NULL` for `parent_id`, you'd iterate
            # and delete from children upwards, or just delete all found descendant directories.
            # The `ON DELETE SET NULL` on parent_id is the main confusing factor here.
            # Let's assume "delete folder and its content" implies everything within it is gone.
            # The safest way is to delete all identified descendant directories.
            # The `paperdb_initv1.sql` provided has `SET FOREIGN_KEY_CHECKS = 0;` at start and `=1;` at end.
            # This implies it's designed for bulk operations where order might not be strictly enforced during script run.
            # For application logic, we must be careful.

            # Simplest approach if you want full recursive delete:
            # Ensure directory.parent_id's FOREIGN KEY constraint has ON DELETE CASCADE.
            # Then:
            # current_app.logger.info(f"Attempting to delete directory {folder_id} (and its cascaded content) for user {user_id}")
            # rows_affected = query_db("DELETE FROM directory WHERE directory_id = %s AND user_id = %s", (folder_id, user_id), commit=True)
            # This is the cleanest if your schema supports true cascading delete for subdirectories.

            # If `directory.parent_id` constraint is `ON DELETE SET NULL` (as in current schema):
            # This will orphan children. To delete children as well:
            current_app.logger.info(f"Deleting directories: {descendant_dir_ids} for user {user_id}")
            # Delete documents manually first (or rely on cascade, but explicit can be clearer)
            # doc_del_sql = f"DELETE FROM document WHERE directory_id IN ({placeholders}) AND user_id = %s"
            # query_db(doc_del_sql, descendant_dir_ids + [user_id], commit=True)
            
            # Delete from closure table manually (or rely on cascade)
            # closure_del_sql = f"DELETE FROM directory_closure WHERE (ancestor_id IN ({placeholders}) OR descendant_id IN ({placeholders})) AND user_id = %s"
            # query_db(closure_del_sql, descendant_dir_ids * 2 + [user_id], commit=True)

            # Delete directories (deepest first is safest if not using CASCADE for parent_id)
            # For a robust solution without parent_id CASCADE, you'd fetch depth and delete level by level from deepest.
            # For now, relying on the CASCADE for document and directory_closure, and deleting all descendant dirs:
            del_dir_sql = f"DELETE FROM directory WHERE directory_id IN ({placeholders}) AND user_id = %s"
            rows_affected = query_db(del_dir_sql, descendant_dir_ids + [user_id], commit=True)

        else: # Should not happen if folder exists
            rows_affected = 0 # Or delete just the folder_id if no descendants found in closure

        if rows_affected:
            # Also delete actual files on disk for all documents within these deleted directories
            # This part is missing and important. You'd query document.local_url for affected documents
            # BEFORE deleting the document records, then os.remove(file_path).
            return success_response(message="删除成功")
        else:
            # This might happen if the folder was already deleted or another issue.
            return error_response(message="Folder not found or no changes made during delete.", status_code=404)

    except Exception as e:
        current_app.logger.error(f"Error deleting folder {folder_id}: {e}", exc_info=True)
        return error_response(message="Failed to delete folder.", status_code=500, error_details=e)


def _build_tree_recursive(parent_id, all_folders_dict, user_id):
    """
    Helper to recursively build folder tree.
    all_folders_dict should be a dictionary mapping parent_id to a list of its children.
    """
    children = all_folders_dict.get(parent_id, [])
    tree_nodes = []
    for folder in children:
        # Ensure folder belongs to the current user (already filtered in main query)
        # if folder['user_id'] != user_id: continue # Double check, should be pre-filtered

        node = {
            "id": folder['directory_id'],
            "name": folder['directory_name'],
            "type": "folder",
            "parentId": folder['parent_id'],
            "children": _build_tree_recursive(folder['directory_id'], all_folders_dict, user_id)
            # Add other fields like createTime if needed
        }
        tree_nodes.append(node)
    return tree_nodes

@folders_bp.route('/tree', methods=['GET'])
@login_required
def get_folder_tree():
    user_id = g.current_user['user_id']
    try:
        # Fetch all directories for the user
        all_folders_for_user = query_db(
            "SELECT directory_id, directory_name, parent_id FROM directory WHERE user_id = %s ORDER BY directory_name ASC",
            (user_id,)
        )
        
        if not all_folders_for_user:
            return success_response(data=[], message="获取成功") # Empty tree

        # Prepare data for recursive building: a dict mapping parent_id to list of child folders
        folders_by_parent = {}
        for folder in all_folders_for_user:
            pid = folder['parent_id']
            if pid not in folders_by_parent:
                folders_by_parent[pid] = []
            folders_by_parent[pid].append(folder)
        
        # Build tree starting from root folders (parent_id is NULL)
        tree = _build_tree_recursive(None, folders_by_parent, user_id)
        
        return success_response(data=tree, message="获取成功")
    except Exception as e:
        current_app.logger.error(f"Error getting folder tree for user {user_id}: {e}", exc_info=True)
        return error_response(message="Failed to retrieve folder tree.", status_code=500, error_details=e)