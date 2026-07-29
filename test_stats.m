% list all .stl and .obj files
stl_files = dir('downloads/**/*.stl');
obj_files = dir('downloads/**/*.obj');
% joint the lists
all_files = [stl_files; obj_files];
% loop through each file and print its name and size
for i = 1:length(all_files)
  if all_files(i).isdir
    continue; % skip directories
  end
  if all_files(i).name(1) == '.'
    continue;
  end
    file_name = [all_files(i).folder filesep all_files(i).name];
    file_size = all_files(i).bytes;
    [V,F] = load_mesh(file_name);
    [V,~,~,F] = remove_duplicate_vertices(V,0,'F',F);
    s = statistics(V,F,'Fast',true);
    fprintf('%d\t%d\t%s\n',(s.num_nonmanifold_vertices>0 | s.num_nonmanifold_edges>0),s.num_boundary_edges>0,file_name);
end

