function make_access_bounds(root, S)
%MAKE_ACCESS_BOUNDS Draw results/access-stability/bounds.png and bounds.pdf from bounds.csv.
%   One row per node, one panel per scenario (a: original, b: widened), same axes.
%   Colour and fill carry the decision: filled blue circle = definite access, filled orange
%   square = definite exclusion, hollow dark grey diamond = unresolved. The decision is also
%   written at the right of each row. A missing upper end runs the line to the right edge.

out = fullfile(root, 'results', 'access-stability');
opts = detectImportOptions(fullfile(out, 'bounds.csv'), 'Delimiter', ',');
opts = setvartype(opts, opts.VariableNames, 'string');
T = readtable(fullfile(out, 'bounds.csv'), opts);
num = @(s) str2double(replace(s, "infinity", "Inf"));
lo = num(T.lower_min); hi = num(T.upper_min); thr = unique(num(T.threshold_min));
assert(isscalar(thr) && ~any(isnan([lo; hi])), 'bounds.csv: unreadable bound or threshold');

% The stored decision must follow the rule: upper <= threshold is access, lower > threshold exclusion.
rule = repmat("unresolved", height(T), 1);
rule(hi <= thr) = "definite_access"; rule(lo > thr) = "definite_exclusion";
assert(all(rule == T.classification), 'bounds.csv: decision disagrees with the threshold rule');

scen = ["original", "widened"];
nodes = T.node(T.scenario == scen(1));
n = numel(nodes);
xmax = max([lo(isfinite(lo)); hi(isfinite(hi)); thr]) * 1.15;
style.definite_access    = struct('c', S.c.blue,   'm', 'o', 'face', S.c.blue,   'word', 'access');
style.definite_exclusion = struct('c', S.c.orange, 'm', 's', 'face', S.c.orange, 'word', 'exclusion');
style.unresolved         = struct('c', S.c.ink,    'm', 'd', 'face', [1 1 1],    'word', 'unresolved');

% Layout in inches: node labels | panel a | decision words | panel b | decision words.
W = 7.2; H = 2.75; left = 0.5; word = 0.78; gap = 0.12; bottom = 0.45; top = 0.3;
pw = (W - left - 2 * word - gap) / 2; ph = H - bottom - top;
fig = figure('Visible', 'off', 'Units', 'inches', 'Position', [1 1 W H]);
for p = 1:2
    ax = axes(fig, 'Units', 'inches', 'Position', [left + (p - 1) * (pw + word + gap), bottom, pw, ph]);
    hold(ax, 'on');
    xline(ax, thr, ':', 'Color', S.c.grey, 'LineWidth', 0.9);
    R = T(T.scenario == scen(p), :);
    assert(isequal(R.node, nodes), 'bounds.csv: node order differs between scenarios');
    for i = 1:n
        y = n + 1 - i;
        a = num(R.lower_min(i)); b = num(R.upper_min(i));
        st = style.(R.classification(i));
        if isinf(a)   % no path: nothing to draw at a finite time
            text(ax, 0, y, 'no path', 'Color', st.c, 'FontSize', S.size.note, ...
                'HorizontalAlignment', 'left', 'VerticalAlignment', 'middle');
        else
            ends = [a, b]; ends(isinf(ends)) = xmax;
            plot(ax, ends, [y y], '-', 'Color', st.c, 'LineWidth', 1.2);
            mk = a; if isfinite(b) && b ~= a, mk = [a b]; end
            plot(ax, mk, y * ones(size(mk)), st.m, 'MarkerSize', 5, 'LineWidth', 1.0, ...
                'MarkerEdgeColor', st.c, 'MarkerFaceColor', st.face);
        end
        text(ax, xmax + 0.04 * xmax, y, st.word, 'Color', st.c, 'FontSize', S.size.note, ...
            'HorizontalAlignment', 'left', 'VerticalAlignment', 'middle', 'Clipping', 'off');
    end
    if p == 1
        text(ax, thr + 0.5, n + 0.55, sprintf('access threshold, %g min', thr), 'Color', S.c.grey, ...
            'FontSize', S.size.tick, 'HorizontalAlignment', 'left', 'VerticalAlignment', 'middle');
    end
    set(ax, 'XLim', [-0.03 * xmax, xmax], 'YLim', [0.45, n + 0.85], 'XTick', 0:5:xmax, ...
        'YTick', 1:n, 'TickLength', [0 0], 'XMinorTick', 'on', 'Layer', 'top');
    ax.XAxis.TickLength = [0.012 0.012];
    ax.XAxis.MinorTickValues = 0:1:floor(xmax);
    ax.XTickLabel = compose('$%d$', ax.XTick);
    if p == 1
        ax.YTickLabel = flip(nodes);
    else
        ax.YTickLabel = {};
    end
    xlabel(ax, 'Shortest travel time to clinic (min)', 'FontSize', S.size.label);
    title(ax, ['\textbf{' char('a' + p - 1) '}'], 'FontSize', S.size.letter, 'Interpreter', 'latex');
    ax.TitleHorizontalAlignment = 'left';
end
export_pair(fig, fullfile(out, 'bounds'));
end
