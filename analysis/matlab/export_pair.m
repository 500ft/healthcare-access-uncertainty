function export_pair(fig, stem)
%EXPORT_PAIR Write a vector PDF and a 300-dpi PNG, then close the figure.
exportgraphics(fig, [stem '.pdf'], 'ContentType', 'vector', 'BackgroundColor', 'white');
exportgraphics(fig, [stem '.png'], 'Resolution', 300, 'BackgroundColor', 'white');
close(fig);
end
