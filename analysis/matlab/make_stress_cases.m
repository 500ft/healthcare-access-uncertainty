function make_stress_cases(root, S)
%MAKE_STRESS_CASES Draw the detector stress-case gallery and the synthetic method demo.
%   Inputs: results/figures/data/<case>.json, written by analysis/plot_stress_cases.py.
%   Outputs: results/figures/0*.png/.pdf and results/method_demo_synthetic.png/.pdf.
%   Grey is the disturbance field (colour bar). Geometry: reference centerline = dark grey
%   pixels, legacy chord = orange dash-dot, delivered path = blue, path endpoints = hollow
%   blue circles. Words other than the key, panel letters and colour bar are in the captions.

dataDir = fullfile(root, 'results', 'figures', 'data');
figDir = fullfile(root, 'results', 'figures');
D = struct();
for name = ["demo_reference", "tight_curve", "wide_corridor", "low_snr", "crossing", ...
            "short_segments", "linear_confound_riverbank"]
    D.(name) = jsondecode(fileread(fullfile(dataDir, name + ".json")));
end
geo = {'reference', 'chord', 'path'};
% Each panel: case, view index, layers drawn over the field.
fig_gallery(S, {{D.demo_reference, 1, {}}, {D.demo_reference, 1, geo}}, geo, ...
    fullfile(figDir, '01_demo_paths_vs_chords'));
fig_gallery(S, {{D.tight_curve, 1, [geo {'ends'}]}}, [geo {'ends'}], ...
    fullfile(figDir, '02_hairpin_chord_vs_path'));
fig_gallery(S, {{D.wide_corridor, 1, [geo {'ends'}]}, {D.wide_corridor, 2, [geo {'ends'}]}}, ...
    [geo {'ends'}], fullfile(figDir, '03_wide_corridor_centred_endpoints'));
fig_gallery(S, {{D.low_snr, 1, {}}, {D.low_snr, 1, geo}}, geo, fullfile(figDir, '04_low_snr_curve'));
fig_gallery(S, {{D.crossing, 1, geo}, {D.short_segments, 1, geo}, ...
    {D.linear_confound_riverbank, 1, geo}}, geo, fullfile(figDir, '05_misses_and_confound'));
fig_gallery(S, {{D.demo_reference, 1, {}}, {D.demo_reference, 1, {'path'}}}, {'path'}, ...
    fullfile(root, 'results', 'method_demo_synthetic'));
end

function fig_gallery(S, panels, keys, stem)
n = numel(panels);
W = 7.2; left = 0.04; right = 0.9; gap = 0.14; bottom = 0.04; letter = 0.22; keyh = 0.24;
pw = (W - left - right - gap * (n - 1)) / n;
v = panels{1}{1}.views(panels{1}{2});
aspect = (diff(v.rows) + 1) / (diff(v.cols) + 1);
ph = pw * aspect;
if n == 1, letter = 0.06; end
H = bottom + ph + letter + keyh;
fig = figure('Visible', 'off', 'Units', 'inches', 'Position', [1 1 W H]);
cmap = linspace(1, 0.35, 256)' * [1 1 1];   % white to mid grey, so dark geometry stays visible
lo = inf; hi = -inf;
for p = 1:n
    [c, k, layers] = panels{p}{:};
    ax = axes(fig, 'Units', 'inches', 'Position', [left + (p - 1) * (pw + gap), bottom, pw, ph]);
    draw_panel(ax, S, c, k, layers, cmap);
    v = c.views(k);
    F = c.field(v.rows(1) - c.origin_px(2) + 1:v.rows(2) - c.origin_px(2) + 1, ...
                v.cols(1) - c.origin_px(1) + 1:v.cols(2) - c.origin_px(1) + 1);
    lo = min(lo, min(F(:))); hi = max(hi, max(F(:)));
    if n > 1
        title(ax, ['\textbf{' char('a' + p - 1) '}'], 'FontSize', S.size.letter, 'Interpreter', 'latex');
        ax.TitleHorizontalAlignment = 'left';
    end
end
r = c.display_range;
cb = colorbar(ax, 'Units', 'inches');
cb.Position = [W - right + 0.12, bottom, 0.11, ph];
ax.Position = [left + (n - 1) * (pw + gap), bottom, pw, ph];
cb.Ticks = r(1):r(2);
cb.TickLabels = compose('$%d$', cb.Ticks);
cb.TickLabelInterpreter = 'latex';
cb.FontSize = S.size.tick;
cb.TickDirection = 'out';
cb.Color = S.c.ink;
cb.Label.String = strrep(c.field_label, 'z units', '$z$ units');
cb.Label.Interpreter = 'latex';
cb.Label.FontSize = S.size.label;
draw_key(fig, S, keys, [left, bottom + ph + letter, W - left - right, keyh]);
export_pair(fig, stem);
fprintf('  %s: field %.2f to %.2f shown on %d to %d\n', stem, lo, hi, r(1), r(2));
end

function draw_panel(ax, S, c, k, layers, cmap)
hold(ax, 'on');
[nr, nc] = size(c.field);
x = c.origin_px(1) + [0, nc - 1]; y = c.origin_px(2) + [0, nr - 1];
image(ax, 'XData', x, 'YData', y, 'CData', c.field, 'CDataMapping', 'scaled');
colormap(ax, cmap);
clim(ax, c.display_range(:)');
if any(strcmp(layers, 'reference')) && ~isempty(c.reference_px)
    M = zeros(nr, nc);
    rp = c.reference_px - c.origin_px(:)' + 1;      % [column row], 1-based in the stored block
    ok = rp(:, 1) >= 1 & rp(:, 1) <= nc & rp(:, 2) >= 1 & rp(:, 2) <= nr;
    M(sub2ind([nr nc], rp(ok, 2), rp(ok, 1))) = 1;
    image(ax, 'XData', x, 'YData', y, 'CData', repmat(reshape(S.c.ink, 1, 1, 3), nr, nc), ...
        'AlphaData', M);
end
cands = c.candidates;
if isstruct(cands)
    for j = 1:numel(cands)
        P = cands(j).path_px; E = cands(j).endpoints_px;
        if any(strcmp(layers, 'chord'))
            plot(ax, E(:, 1), E(:, 2), '-.', 'Color', S.c.orange, 'LineWidth', 1.0);
        end
        if any(strcmp(layers, 'path'))
            plot(ax, P(:, 1), P(:, 2), '-', 'Color', S.c.blue, 'LineWidth', 1.3);
        end
        if any(strcmp(layers, 'ends'))
            plot(ax, P([1 end], 1), P([1 end], 2), 'o', 'MarkerSize', 4.5, 'LineWidth', 1.0, ...
                'MarkerEdgeColor', S.c.blue, 'MarkerFaceColor', 'w');
        end
    end
end
v = c.views(k);
set(ax, 'YDir', 'reverse', 'XLim', v.cols(:)' + [-0.5 0.5], 'YLim', v.rows(:)' + [-0.5 0.5], ...
    'XTick', [], 'YTick', [], 'Box', 'on', 'Layer', 'top', 'DataAspectRatio', [1 1 1]);
end

function draw_key(fig, S, keys, pos)
%DRAW_KEY One row of line samples, each labelled in its own colour, centred above the panels.
ax = axes(fig, 'Units', 'inches', 'Position', pos, 'Visible', 'off', 'XLim', [0 pos(3)], 'YLim', [0 1]);
hold(ax, 'on');
spec.reference = {'-', S.c.ink, 0.9, 'none', 'reference centerline'};
spec.chord = {'-.', S.c.orange, 1.0, 'none', 'legacy chord'};
spec.path = {'-', S.c.blue, 1.3, 'none', 'delivered path'};
spec.ends = {'none', S.c.blue, 1.0, 'o', 'path endpoint'};
x = 0; h = gobjects(0); y = 0.5;
for i = 1:numel(keys)
    s = spec.(keys{i});
    if strcmp(s{4}, 'o')
        h(end + 1) = plot(ax, x + 0.15, y, 'o', 'MarkerSize', 4.5, 'LineWidth', 1.0, ...
            'MarkerEdgeColor', s{2}, 'MarkerFaceColor', 'w'); %#ok<AGROW>
    else
        h(end + 1) = plot(ax, x + [0 0.3], [y y], s{1}, 'Color', s{2}, 'LineWidth', s{3}); %#ok<AGROW>
    end
    t = text(ax, x + 0.37, y, s{5}, 'Color', s{2}, 'FontSize', S.size.note, ...
        'VerticalAlignment', 'middle', 'HorizontalAlignment', 'left');
    h(end + 1) = t; %#ok<AGROW>
    x = x + 0.37 + t.Extent(3) + 0.3;
end
shift = (pos(3) - (x - 0.3)) / 2;
for g = h
    if isa(g, 'matlab.graphics.primitive.Text')
        g.Position(1) = g.Position(1) + shift;
    else
        g.XData = g.XData + shift;
    end
end
end
