from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from qgis.core import QgsPalettedRasterRenderer, QgsProcessingUtils, QgsProject
from qgis.PyQt.QtWidgets import QDockWidget
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface

# -----------------------------------------------------------------------------------
# Función para obtener los valores de "Identify Results" como un diccionario.
# -----------------------------------------------------------------------------------
def get_identify_results_as_dict():
    """
    Navega por los resultados de identificación en la ventana de QGIS 
    y devuelve los valores en un diccionario.

    :return: Diccionario con números de banda como claves y valores identificados como valores.
    """
    results = {}
    
    # Buscar todos los QDockWidgets en la interfaz de QGIS
    for dock in iface.mainWindow().findChildren(QDockWidget):
        if "Identify Results" in dock.windowTitle():
            tree = dock.findChild(QTreeView)
            if tree:
                model = tree.model()
                for index in range(model.rowCount()):
                    parent = model.index(index, 0)
                    for child_index in range(model.rowCount(parent)):
                        feature = model.index(child_index, 0, parent)
                        for grandchild_index in range(model.rowCount(feature)):
                            field = model.index(grandchild_index, 0, feature)
                            field_name = model.data(field)
                            value = model.index(grandchild_index, 1, feature)
                            value_data = model.data(value)
                            
                            # Extraer el número de banda y su valor asociado
                            if "Band" in field_name:
                                band_num = int(field_name.split('_')[1])
                                results[band_num] = int(value_data)

    return results

# -----------------------------------------------------------------------------------
# Función para configurar la simbología de una capa raster
# -----------------------------------------------------------------------------------
def set_paletted_symbology(layer):
    """
    Configura la simbología paletted para una capa raster.

    :param layer: Capa raster a configurar.
    """
    # Definir clases de color para la simbología
    classes = [
        QgsPalettedRasterRenderer.Class(0, QColor(0, 0, 0, 0), "Zonas de no Scribble"),   # Transparente
        QgsPalettedRasterRenderer.Class(1, QColor(255, 0, 0), "Zonas para Scribble")   # Rojo
    ]

    # Establecer el renderizador
    renderer = QgsPalettedRasterRenderer(layer.dataProvider(), 1, classes)
    layer.setRenderer(renderer)
    
    # Refrescar la capa
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())

# -----------------------------------------------------------------------------------
# Función para filtrar un raster según valores y un rango definido.
# -----------------------------------------------------------------------------------
def filter_raster_by_value(raster_name, value_range, identified_values):
    """
    Filtra un raster según un conjunto de valores y un rango definido.

    :param raster_name: Nombre de la capa raster en QGIS.
    :param value_range: Rango de valores para el filtro.
    :param identified_values: Diccionario con los valores identificados para filtrar.
    """
    # Obtener la capa raster por su nombre
    s2_layer = QgsProject.instance().mapLayersByName(raster_name)[0]

    # Construir la condición para cada banda usando el rango de valores
    conditions = []
    for band, value in identified_values.items():
        lower_bound = value - value_range
        upper_bound = value + value_range
        conditions.append(f'("{raster_name}@{band}" > {lower_bound} AND "{raster_name}@{band}" < {upper_bound})')

    # Combinar todas las condiciones en una expresión
    expression = ' AND '.join(conditions)

    # Crear una lista de QgsRasterCalculatorEntry para todas las bandas
    entries = []
    for band in range(1, s2_layer.bandCount() + 1):
        entry = QgsRasterCalculatorEntry()
        entry.ref = f"{raster_name}@{band}"
        entry.raster = s2_layer
        entry.bandNumber = band
        entries.append(entry)

    # Especificar la ruta temporal para el resultado
    output_path = QgsProcessingUtils.generateTempFilename('filtered.tif')

    # Ejecutar QgsRasterCalculator
    calculator = QgsRasterCalculator(expression, output_path, 'GTiff', s2_layer.extent(), s2_layer.width(), s2_layer.height(), entries)
    calculator.processCalculation()

    # Añadir el raster resultante al proyecto de QGIS y configurar la simbología
    layer_name = "Máscara"
    iface.addRasterLayer(output_path, layer_name)
    filtered_layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    set_paletted_symbology(filtered_layer)
    iface.setActiveLayer(filtered_layer)  # Establecer la capa resultante como activa

# -----------------------------------------------------------------------------------
# Ejecución de las funciones
# -----------------------------------------------------------------------------------

# Obtener los valores identificados
identified_values_example = get_identify_results_as_dict()

# Filtrar el raster y configurar la simbología
all_layers = QgsProject.instance().mapLayers().values()
s2_layers = [layer.name() for layer in all_layers if layer.name().startswith("S2")]
filter_raster_by_value(s2_layers[0], 900, identified_values_example)