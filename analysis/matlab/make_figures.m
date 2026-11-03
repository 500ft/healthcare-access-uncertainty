% MAKE_FIGURES Draw every data figure and typeset-table fragment in this repository.
%   Run from analysis/matlab:   matlab -batch make_figures
%   Reads committed data only (results/access-stability/bounds.csv, the qualification record and
%   results/figures/data/*.json) and writes each PNG (300 dpi) with a vector PDF beside it.
%   Typeset the two .tex table fragments afterwards as described in README.md.

here = fileparts(mfilename('fullpath'));
root = fileparts(fileparts(here));
addpath(here);
S = fig_style();
jobs = {'make_access_bounds', @() make_access_bounds(root, S); ...
        'make_access_tables', @() make_access_tables(root, S); ...
        'make_stress_cases',  @() make_stress_cases(root, S)};
failed = 0;
for k = 1:size(jobs, 1)
    try
        jobs{k, 2}();
        fprintf('ok %s\n', jobs{k, 1});
    catch err
        failed = failed + 1;
        fprintf('FAILED %s: %s\n', jobs{k, 1}, getReport(err, 'extended', 'hyperlinks', 'off'));
    end
end
if failed
    error('make_figures:failed', '%d generator(s) failed', failed);
end
