from qgis.core import QgsMultiBandColorRenderer, QgsContrastEnhancement, QgsProject

# -----------------------------------------------------------------------------------
# Función para configurar la visualización RGB de una capa raster.
# Esta función crea una nueva capa para cada configuración de visualización.
# -----------------------------------------------------------------------------------
def set_rgb_rendering(layer, red_band, green_band, blue_band, name_suffix):
    """
    Configura la visualización RGB de la capa y crea una copia de la capa con 
    la nueva configuración de visualización.

    :param layer: Capa a configurar.
    :param red_band: Índice de la banda para el rojo.
    :param green_band: Índice de la banda para el verde.
    :param blue_band: Índice de la banda para el azul.
    :param name_suffix: Sufijo para el nombre de la capa clonada.
    """
    
    # Establecer el renderizador multibanda
    new_renderer = QgsMultiBandColorRenderer(layer.dataProvider(), red_band, green_band, blue_band)
    layer.setRenderer(new_renderer)
    
    # Ajustar el contraste de la capa
    layer.setContrastEnhancement(QgsContrastEnhancement.StretchToMinimumMaximum, True)
    layer.triggerRepaint()
    
    # Duplicar la capa y añadirla al proyecto con un nuevo nombre
    clone = layer.clone()
    clone.setName(layer.name() + name_suffix)
    QgsProject.instance().addMapLayer(clone)

# -----------------------------------------------------------------------------------
# Ejecución de la función
# -----------------------------------------------------------------------------------

# Obtener la capa con nombre "S2"
s2_layer = QgsProject.instance().mapLayersByName("S2")[0]

# Aplicar diferentes configuraciones RGB a la capa
set_rgb_rendering(s2_layer, 4, 3, 2, "_NaturalColor")
set_rgb_rendering(s2_layer, 8, 4, 3, "_FalsoColor")
set_rgb_rendering(s2_layer, 9, 12, 4, "_InfrarrojoOndaCorta")
set_rgb_rendering(s2_layer, 11, 8, 2, "_Agricultura")