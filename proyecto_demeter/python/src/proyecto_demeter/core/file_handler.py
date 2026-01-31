"""
MÓDULO MODERNO DE GESTIÓN DE ARCHIVOS - VERSIÓN INDEPENDIENTE

Este módulo proporciona funcionalidades modernizadas para:
- Operaciones de archivos sin dependencias externas
- Gestión segura de copias, movimientos y backups
- Búsqueda y filtrado inteligente de archivos
- Organización automática por tipo y contenido
- Manejo de metadatos y propiedades de archivos

ÍNDICE DE FUNCIONES:
--------------------
CLASE FileSystemManager:
1.  __init__(self, base_dir: Optional[Union[str, Path]] = None) -> None
    Inicializa el gestor de archivos con directorio base.

2.  find_files(self, patterns: List[str], directory: Optional[Union[str, Path]] = None,
               recursive: bool = True, min_size: int = 0) -> List[Path]
    Busca archivos por múltiples criterios.

3.  find_excel_files(self, directory: Optional[Union[str, Path]] = None,
                     recursive: bool = True) -> List[Path]
    Busca específicamente archivos Excel.

4.  find_by_content(self, directory: Union[str, Path], content_pattern: str,
                    file_pattern: str = "*") -> List[Path]
    Busca archivos por contenido dentro del texto.

5.  safe_copy(self, source: Union[str, Path], destination: Union[str, Path],
              overwrite: bool = False, preserve_metadata: bool = True) -> Path
    Copia segura con manejo de conflictos y metadatos.

6.  safe_move(self, source: Union[str, Path], destination: Union[str, Path],
              overwrite: bool = False) -> Path
    Mueve archivos de forma segura.

7.  backup_file(self, source: Union[str, Path], backup_name: Optional[str] = None,
                versioned: bool = True) -> Path
    Crea copias de seguridad versionadas.

8.  get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]
    Obtiene información detallada del archivo.

9.  get_file_metadata(self, file_path: Union[str, Path]) -> Dict[str, Any]
    Obtiene metadatos específicos del archivo.

10. clean_filename(self, filename: str, max_length: int = 255,
                   replace_spaces: bool = True) -> str
    Limpia nombre de archivo para compatibilidad multiplataforma.

11. generate_unique_filename(self, base_path: Union[str, Path],
                             with_timestamp: bool = False) -> Path
    Genera nombre de archivo único.

12. delete_old_files(self, directory: Union[str, Path], pattern: str,
                     days_old: int = 30, dry_run: bool = False) -> List[Path]
    Elimina archivos antiguos con modo prueba.

13. organize_files_by_extension(self, source_dir: Union[str, Path],
                                target_dir: Optional[Union[str, Path]] = None,
                                move: bool = True) -> Dict[str, List[Path]]
    Organiza archivos por extensión.

14. organize_files_by_date(self, source_dir: Union[str, Path],
                           date_format: str = "%Y/%m",
                           target_dir: Optional[Union[str, Path]] = None) -> Dict[str, List[Path]]
    Organiza archivos por fecha de modificación.

15. validate_file_integrity(self, file_path: Union[str, Path]) -> Dict[str, Any]
    Valida integridad y accesibilidad de archivo.

16. compare_files(self, file1: Union[str, Path], file2: Union[str, Path],
                  quick: bool = True) -> Dict[str, Any]
    Compara dos archivos por contenido y propiedades.

17. get_directory_files_summary(self, directory: Union[str, Path],
                                group_by: str = "extension") -> Dict[str, Any]
    Obtiene resumen de archivos en directorio.

18. batch_rename(self, directory: Union[str, Path], pattern: str,
                 replacement: str, dry_run: bool = True) -> List[Dict[str, str]]
    Renombra archivos por lotes con patrón.

19. calculate_hash(self, file_path: Union[str, Path],
                   algorithm: str = "md5") -> str
    Calcula hash criptográfico de archivo.

20. compress_file(self, source: Union[str, Path], destination: Optional[Union[str, Path]] = None,
                  format: str = "zip") -> Path
    Comprime archivo individual.

21. extract_file(self, archive_path: Union[str, Path],
                 destination: Optional[Union[str, Path]] = None) -> Path
    Extrae archivo comprimido.

22. monitor_directory_changes(self, directory: Union[str, Path],
                              callback: callable, interval: int = 5) -> None
    Monitorea cambios en directorio.

23. create_nested_structure(self, structure: Dict, base_dir: Optional[Path] = None) -> Dict[str, Path]
    Crea estructura anidada de directorios desde diccionario.

24. get_file_encoding(self, file_path: Path) -> str
    Detecta encoding de archivo de texto.

25. is_binary_file(self, file_path: Path) -> bool
    Verifica si un archivo es binario.

26. get_mime_type(self, file_path: Path) -> str
    Obtiene tipo MIME de archivo.

FUNCIONES AUXILIARES DEL MÓDULO:
27. expand_path_variables(path_str: str) -> str
    Expande variables de entorno y usuario en una ruta.

28. is_valid_path_syntax(path_str: str) -> bool
    Verifica si una cadena tiene sintaxis de ruta válida.

29. safe_path_join(base: Union[str, Path], *parts: str) -> Path
    Une rutas de forma segura previniendo path traversal.
"""

import os
import shutil
import hashlib
import zipfile
import time
import mimetypes
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Union, Any, Callable, Tuple
import json


class FileSystemManager:
    """
    Gestor moderno de sistema de archivos con operaciones seguras
    y avanzadas, completamente independiente sin dependencias externas.
    """
    
    # ============================================================================
    # FUNCIÓN 1: Inicialización
    # ============================================================================
    def __init__(self, base_dir: Optional[Union[str, Path]] = None) -> None:
        """
        Inicializa el gestor de archivos con directorio base.
        
        Args:
            base_dir: Directorio base para operaciones (default: directorio actual)
        """
        self.base_dir = self._resolve_path(base_dir) if base_dir else Path.cwd().resolve()
        
        # Configurar tipos MIME
        mimetypes.init()
        
        # Estructura de workspace (se inicializa explícitamente vía setup_workspace)
        self.workspace_structure = {}
    
    # ============================================================================
    
    # ============================================================================
    # FUNCIÓN 2: Buscar archivos
    # ============================================================================
    def find_files(self, 
                   patterns: List[str], 
                   directory: Optional[Union[str, Path]] = None,
                   recursive: bool = True, 
                   min_size: int = 0) -> List[Path]:
        """
        Busca archivos por múltiples criterios.
        
        Args:
            patterns: Lista de patrones (ej: ["*.txt", "*.csv"])
            directory: Directorio donde buscar (default: directorio base)
            recursive: Si True, busca en subdirectorios
            min_size: Tamaño mínimo en bytes (0 = sin límite)
            
        Returns:
            Lista de Paths de archivos encontrados, ordenados
        """
        if directory is None:
            directory = self.base_dir
        
        dir_path = self._resolve_path(directory)
        
        if not dir_path.exists() or not dir_path.is_dir():
            return []
        
        files = []
        search_method = dir_path.rglob if recursive else dir_path.glob
        
        for pattern in patterns:
            try:
                for file_path in search_method(pattern):
                    if file_path.is_file():
                        # Filtrar por tamaño mínimo
                        if min_size > 0:
                            try:
                                if file_path.stat().st_size < min_size:
                                    continue
                            except (OSError, PermissionError):
                                continue
                        
                        # Excluir archivos temporales y ocultos
                        if not file_path.name.startswith(('~$', '.', '__')):
                            files.append(file_path)
            except Exception:
                continue
        
        # Ordenar por nombre, luego por tamaño
        files.sort(key=lambda x: (x.name.lower(), x.stat().st_size if x.exists() else 0))
        
        return files
    
    # ============================================================================
    # FUNCIÓN 3: Buscar archivos Excel
    # ============================================================================
    def find_excel_files(self, 
                         directory: Optional[Union[str, Path]] = None,
                         recursive: bool = True) -> List[Path]:
        """
        Busca específicamente archivos Excel.
        
        Args:
            directory: Directorio donde buscar (default: directorio base)
            recursive: Si True, busca en subdirectorios
            
        Returns:
            Lista de Paths de archivos Excel encontrados
        """
        patterns = ["*.xls", "*.xlsx", "*.XLS", "*.XLSX"]
        return self.find_files(patterns, directory, recursive)
    
    # ============================================================================
    # FUNCIÓN 4: Buscar por contenido
    # ============================================================================
    def find_by_content(self, 
                        directory: Union[str, Path], 
                        content_pattern: str,
                        file_pattern: str = "*") -> List[Path]:
        """
        Busca archivos por contenido dentro del texto.
        
        Args:
            directory: Directorio donde buscar
            content_pattern: Patrón regex a buscar en contenido
            file_pattern: Patrón para nombres de archivo
            
        Returns:
            Lista de Paths de archivos que contienen el patrón
        """
        dir_path = self._resolve_path(directory)
        
        if not dir_path.exists() or not dir_path.is_dir():
            return []
        
        matching_files = []
        regex = re.compile(content_pattern, re.IGNORECASE)
        
        for file_path in dir_path.rglob(file_pattern):
            if not file_path.is_file():
                continue
            
            # Verificar si es archivo de texto
            if self._is_text_file(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(100000)  # Leer primeros 100KB
                        
                        if regex.search(content):
                            matching_files.append(file_path)
                except (UnicodeDecodeError, PermissionError, OSError):
                    continue
        
        return matching_files
    
    # ============================================================================
    # FUNCIÓN 5: Copia segura
    # ============================================================================
    def safe_copy(self, 
                  source: Union[str, Path], 
                  destination: Union[str, Path],
                  overwrite: bool = False, 
                  preserve_metadata: bool = True) -> Path:
        """
        Copia segura con manejo de conflictos y metadatos.
        
        Args:
            source: Archivo fuente
            destination: Destino deseado
            overwrite: Si True, sobrescribe si existe
            preserve_metadata: Si True, preserva metadatos
            
        Returns:
            Path donde se copió finalmente el archivo
            
        Raises:
            FileNotFoundError: Si el archivo fuente no existe
            ValueError: Si las rutas no son seguras
        """
        src_path = self._resolve_path(source, must_exist=True)
        dst_path = self._resolve_path(destination)
        
        # Validar que sea archivo
        if not src_path.is_file():
            raise ValueError(f"La ruta fuente no es un archivo: {src_path}")
        
        # Validar seguridad (que esté dentro del directorio base)
        if not self._is_within_base(dst_path.parent):
            raise ValueError(f"Destino fuera del directorio base: {dst_path}")
        
        # Si no se permite sobrescribir, generar nombre único
        if not overwrite and dst_path.exists():
            dst_path = self._make_unique_path(dst_path)
        
        # Crear directorio destino si no existe
        self._ensure_directory(dst_path.parent)
        
        # Copiar archivo
        if preserve_metadata:
            shutil.copy2(src_path, dst_path)
        else:
            shutil.copy(src_path, dst_path)
        
        return dst_path
    
    # ============================================================================
    # FUNCIÓN 6: Mover de forma segura
    # ============================================================================
    def safe_move(self, 
                  source: Union[str, Path], 
                  destination: Union[str, Path],
                  overwrite: bool = False) -> Path:
        """
        Mueve archivos de forma segura.
        
        Args:
            source: Archivo fuente
            destination: Destino deseado
            overwrite: Si True, sobrescribe si existe
            
        Returns:
            Path donde se movió finalmente el archivo
        """
        src_path = self._resolve_path(source, must_exist=True)
        dst_path = self._resolve_path(destination)
        
        if not src_path.is_file():
            raise ValueError(f"La ruta fuente no es un archivo: {src_path}")
        
        # Validar seguridad
        if not self._is_within_base(dst_path.parent):
            raise ValueError(f"Destino fuera del directorio base: {dst_path}")
        
        # Si no se permite sobrescribir, generar nombre único
        if not overwrite and dst_path.exists():
            dst_path = self._make_unique_path(dst_path)
        
        # Crear directorio destino si no existe
        self._ensure_directory(dst_path.parent)
        
        # Mover archivo
        shutil.move(str(src_path), str(dst_path))
        
        return dst_path
    
    # ============================================================================
    # FUNCIÓN 7: Crear backup
    # ============================================================================
    def backup_file(self, 
                    source: Union[str, Path], 
                    backup_name: Optional[str] = None,
                    versioned: bool = True) -> Path:
        """
        Crea copias de seguridad versionadas.
        
        Args:
            source: Archivo a respaldar
            backup_name: Nombre personalizado para backup (opcional)
            versioned: Si True, añade timestamp al nombre
            
        Returns:
            Path del archivo de backup creado
        """
        src_path = self._resolve_path(source, must_exist=True)
        
        if not src_path.is_file():
            raise ValueError(f"La ruta no es un archivo: {src_path}")
        
        # Usar directorio de backups del workspace
        backup_dir = self.workspace_structure.get('backups')
        if not backup_dir:
            backup_dir = self.base_dir / 'Backups'
            self._ensure_directory(backup_dir)
        
        # Generar nombre de backup
        if backup_name:
            backup_stem = backup_name
        else:
            backup_stem = src_path.stem
        
        if versioned:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{backup_stem}_v{timestamp}{src_path.suffix}"
        else:
            backup_filename = f"{backup_stem}_backup{src_path.suffix}"
        
        backup_path = backup_dir / backup_filename
        
        # Copiar con metadatos
        return self.safe_copy(src_path, backup_path, overwrite=False, preserve_metadata=True)
    
    # ============================================================================
    # FUNCIÓN 8: Obtener información de archivo
    # ============================================================================
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Obtiene información detallada del archivo.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Diccionario con información del archivo
        """
        path_obj = self._resolve_path(file_path)
        
        if not path_obj.exists() or not path_obj.is_file():
            return {"error": "Archivo no encontrado o no es archivo"}
        
        stat = path_obj.stat()
        file_size = stat.st_size
        
        info = {
            'basic_info': self.get_path_info(path_obj),
            'size': {
                'bytes': file_size,
                'kb': round(file_size / 1024, 2),
                'mb': round(file_size / (1024 * 1024), 4),
                'gb': round(file_size / (1024 * 1024 * 1024), 6)
            },
            'timestamps': {
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'accessed': datetime.fromtimestamp(stat.st_atime)
            },
            'permissions': {
                'readable': os.access(path_obj, os.R_OK),
                'writable': os.access(path_obj, os.W_OK),
                'executable': os.access(path_obj, os.X_OK)
            },
            'type_info': {
                'mime_type': self.get_mime_type(path_obj),
                'is_binary': self.is_binary_file(path_obj),
                'is_text': self._is_text_file(path_obj)
            },
            'hash': {
                'md5': self.calculate_hash(path_obj, 'md5'),
                'sha1': self.calculate_hash(path_obj, 'sha1') if file_size < 100000000 else "TOO_LARGE"
            }
        }
        
        return info
    
    # ============================================================================
    # FUNCIÓN 9: Obtener metadatos
    # ============================================================================
    def get_file_metadata(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Obtiene metadatos específicos del archivo.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Diccionario con metadatos
        """
        info = self.get_file_info(file_path)
        
        # Extraer solo metadatos relevantes
        metadata = {
            'filename': info['basic_info']['name'],
            'path': info['basic_info']['resolved'],
            'size_bytes': info['size']['bytes'],
            'size_human': f"{info['size']['mb']:.2f} MB",
            'created': info['timestamps']['created'].isoformat(),
            'modified': info['timestamps']['modified'].isoformat(),
            'mime_type': info['type_info']['mime_type'],
            'hash_md5': info['hash']['md5'],
            'permissions': info['permissions']
        }
        
        return metadata
    
    # ============================================================================
    # FUNCIÓN 10: Limpiar nombre de archivo
    # ============================================================================
    def clean_filename(self, 
                       filename: str, 
                       max_length: int = 255,
                       replace_spaces: bool = True) -> str:
        """
        Limpia nombre de archivo para compatibilidad multiplataforma.
        
        Args:
            filename: Nombre de archivo a limpiar
            max_length: Longitud máxima permitida
            replace_spaces: Si True, reemplaza espacios con guiones bajos
            
        Returns:
            Nombre de archivo limpio
        """
        # Caracteres prohibidos en Windows, Linux y macOS
        invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
        
        # Eliminar caracteres inválidos
        clean = re.sub(invalid_chars, '_', filename)
        
        # Normalizar espacios
        if replace_spaces:
            clean = re.sub(r'\s+', '_', clean)
        
        # Eliminar múltiples guiones bajos consecutivos
        clean = re.sub(r'_+', '_', clean)
        
        # Eliminar guiones bajos al inicio y final
        clean = clean.strip('_')
        
        # Reemplazar puntos múltiples (excepto extensión)
        name_parts = clean.rsplit('.', 1)
        if len(name_parts) == 2:
            stem = re.sub(r'\.+', '.', name_parts[0])
            clean = f"{stem}.{name_parts[1]}"
        else:
            clean = re.sub(r'\.+', '.', clean)
        
        # Limitar longitud
        if len(clean) > max_length:
            if '.' in clean:
                stem, ext = clean.rsplit('.', 1)
                # Mantener extensión completa
                stem_max = max_length - len(ext) - 1
                if stem_max > 10:  # Al menos 10 caracteres para el nombre
                    clean = f"{stem[:stem_max]}.{ext}"
                else:
                    clean = f"{stem[:10]}.{ext}"
            else:
                clean = clean[:max_length]
        
        # Asegurar que no esté vacío
        if not clean:
            clean = "unnamed_file"
        
        return clean
    
    # ============================================================================
    # FUNCIÓN 11: Generar nombre único
    # ============================================================================
    def generate_unique_filename(self, 
                                 base_path: Union[str, Path],
                                 with_timestamp: bool = False) -> Path:
        """
        Genera nombre de archivo único.
        
        Args:
            base_path: Ruta base deseada
            with_timestamp: Si True, incluye timestamp en lugar de número
            
        Returns:
            Path único que no existe
        """
        path_obj = self._resolve_path(base_path)
        
        if not path_obj.exists():
            return path_obj
        
        if with_timestamp:
            # Usar timestamp de microsegundos
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            stem = path_obj.stem
            suffix = path_obj.suffix
            parent = path_obj.parent
            
            new_name = f"{stem}_{timestamp}{suffix}"
            new_path = parent / new_name
            
            return new_path
        else:
            # Usar método interno
            return self._make_unique_path(path_obj)
    
    # ============================================================================
    # FUNCIÓN 12: Eliminar archivos antiguos
    # ============================================================================
    def delete_old_files(self, 
                         directory: Union[str, Path], 
                         pattern: str,
                         days_old: int = 30, 
                         dry_run: bool = False) -> List[Path]:
        """
        Elimina archivos antiguos con modo prueba.
        
        Args:
            directory: Directorio donde buscar
            pattern: Patrón de archivos (ej: "*.tmp", "backup_*")
            days_old: Archivos más antiguos que estos días se eliminan
            dry_run: Si True, solo muestra lo que se eliminaría
            
        Returns:
            Lista de archivos eliminados (o que se eliminarían)
        """
        dir_path = self._resolve_path(directory)
        
        if not dir_path.exists() or not dir_path.is_dir():
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        files_to_delete = []
        
        for file_path in dir_path.rglob(pattern):
            if file_path.is_file():
                try:
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        files_to_delete.append(file_path)
                except (OSError, PermissionError):
                    continue
        
        deleted_files = []
        
        if dry_run:
            print(f"Modo prueba - Archivos a eliminar ({len(files_to_delete)}):")
            for file_path in files_to_delete:
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                age_days = (datetime.now() - file_mtime).days
                print(f"  {file_path.name} ({age_days} días)")
            deleted_files = files_to_delete
        else:
            for file_path in files_to_delete:
                try:
                    file_path.unlink()
                    deleted_files.append(file_path)
                except Exception as e:
                    print(f"Error eliminando {file_path.name}: {e}")
        
        return deleted_files
    
    # ============================================================================
    # FUNCIÓN 13: Organizar por extensión
    # ============================================================================
    def organize_files_by_extension(self, 
                                    source_dir: Union[str, Path],
                                    target_dir: Optional[Union[str, Path]] = None,
                                    move: bool = True) -> Dict[str, List[Path]]:
        """
        Organiza archivos por extensión.
        
        Args:
            source_dir: Directorio fuente
            target_dir: Directorio destino (default: mismo que fuente)
            move: Si True, mueve archivos; si False, copia
            
        Returns:
            Diccionario con extensiones como clave y listas de archivos
        """
        src_path = self._resolve_path(source_dir, must_exist=True)
        
        if target_dir is None:
            target_path = src_path
        else:
            target_path = self._resolve_path(target_dir)
        
        if not src_path.is_dir():
            raise ValueError(f"Directorio fuente no encontrado: {src_path}")
        
        organized = {}
        
        for file_path in src_path.iterdir():
            if file_path.is_file():
                # Obtener extensión (en minúsculas, sin punto)
                extension = file_path.suffix.lower()
                if extension:
                    extension = extension[1:]  # Quitar punto
                else:
                    extension = "sin_extension"
                
                # Crear directorio para esta extensión
                ext_dir = target_path / extension
                self._ensure_directory(ext_dir)
                
                # Ruta destino
                dest_path = ext_dir / file_path.name
                
                try:
                    if move:
                        # Mover archivo
                        shutil.move(str(file_path), str(dest_path))
                    else:
                        # Copiar archivo
                        shutil.copy2(file_path, dest_path)
                    
                    # Registrar en diccionario
                    if extension not in organized:
                        organized[extension] = []
                    organized[extension].append(dest_path)
                    
                except Exception as e:
                    print(f"Error procesando {file_path.name}: {e}")
        
        return organized
    
    # ============================================================================
    # FUNCIÓN 14: Organizar por fecha
    # ============================================================================
    def organize_files_by_date(self, 
                               source_dir: Union[str, Path],
                               date_format: str = "%Y/%m",
                               target_dir: Optional[Union[str, Path]] = None) -> Dict[str, List[Path]]:
        """
        Organiza archivos por fecha de modificación.
        
        Args:
            source_dir: Directorio fuente
            date_format: Formato de fecha para estructura de directorios
            target_dir: Directorio destino (default: mismo que fuente)
            
        Returns:
            Diccionario con fechas como clave y listas de archivos
        """
        src_path = self._resolve_path(source_dir, must_exist=True)
        
        if target_dir is None:
            target_path = src_path
        else:
            target_path = self._resolve_path(target_dir)
        
        organized = {}
        
        for file_path in src_path.iterdir():
            if file_path.is_file():
                try:
                    # Obtener fecha de modificación
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    date_str = mtime.strftime(date_format)
                    
                    # Crear estructura de directorios por fecha
                    date_dir = target_path / date_str
                    self._ensure_directory(date_dir)
                    
                    # Mover archivo
                    dest_path = date_dir / file_path.name
                    shutil.move(str(file_path), str(dest_path))
                    
                    # Registrar
                    if date_str not in organized:
                        organized[date_str] = []
                    organized[date_str].append(dest_path)
                    
                except Exception as e:
                    print(f"Error organizando {file_path.name}: {e}")
        
        return organized
    
    # ============================================================================
    # FUNCIÓN 15: Validar integridad
    # ============================================================================
    def validate_file_integrity(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Valida integridad y accesibilidad de archivo.
        
        Args:
            file_path: Ruta del archivo a validar
            
        Returns:
            Diccionario con resultados de validación
        """
        path_obj = self._resolve_path(file_path)
        
        checks = {
            'exists': path_obj.exists(),
            'is_file': path_obj.is_file() if path_obj.exists() else False,
            'readable': False,
            'writable': False,
            'size_valid': False,
            'hash_stable': False
        }
        
        if checks['exists'] and checks['is_file']:
            try:
                # Verificar permisos
                checks['readable'] = os.access(path_obj, os.R_OK)
                checks['writable'] = os.access(path_obj, os.W_OK)
                
                # Verificar tamaño
                size = path_obj.stat().st_size
                checks['size_valid'] = size > 0 and size < 10 * 1024 * 1024 * 1024  # < 10GB
                
                # Verificar hash estable (leer dos veces)
                if checks['readable'] and size < 100 * 1024 * 1024:  # < 100MB
                    hash1 = self.calculate_hash(path_obj, 'md5')
                    time.sleep(0.1)  # Pequeña pausa
                    hash2 = self.calculate_hash(path_obj, 'md5')
                    checks['hash_stable'] = hash1 == hash2
                    checks['current_hash'] = hash1
                
            except (OSError, PermissionError):
                pass
        
        # Calcular puntuación de integridad
        passed = sum(1 for check in checks.values() if check is True)
        total = len([v for v in checks.values() if isinstance(v, bool)])
        checks['integrity_score'] = f"{passed}/{total}"
        checks['is_valid'] = checks['exists'] and checks['is_file'] and checks['readable']
        
        return checks
    
    # ============================================================================
    # FUNCIÓN 16: Comparar archivos
    # ============================================================================
    def compare_files(self, 
                      file1: Union[str, Path], 
                      file2: Union[str, Path],
                      quick: bool = True) -> Dict[str, Any]:
        """
        Compara dos archivos por contenido y propiedades.
        
        Args:
            file1: Primer archivo
            file2: Segundo archivo
            quick: Si True, solo compara tamaño y hash rápido
            
        Returns:
            Diccionario con resultados de comparación
        """
        path1 = self._resolve_path(file1)
        path2 = self._resolve_path(file2)
        
        result = {
            'file1': str(path1),
            'file2': str(path2),
            'both_exist': path1.exists() and path2.exists(),
            'identical': False,
            'differences': []
        }
        
        if not result['both_exist']:
            if not path1.exists():
                result['differences'].append("file1 no existe")
            if not path2.exists():
                result['differences'].append("file2 no existe")
            return result
        
        # Obtener información básica
        info1 = self.get_file_info(path1)
        info2 = self.get_file_info(path2)
        
        # Comparar propiedades básicas
        if info1['size']['bytes'] != info2['size']['bytes']:
            result['differences'].append(f"Tamaño diferente: {info1['size']['bytes']} vs {info2['size']['bytes']}")
        
        if info1['timestamps']['modified'] != info2['timestamps']['modified']:
            result['differences'].append(f"Fecha modificación diferente")
        
        # Comparar hash (comparación rápida de contenido)
        if info1['hash']['md5'] != info2['hash']['md5']:
            result['differences'].append("Contenido diferente (hash MD5 no coincide)")
        
        # Si quick=False, comparación línea por línea (solo para archivos de texto pequeños)
        if not quick and not result['differences']:
            if info1['type_info']['is_text'] and info2['type_info']['is_text']:
                if info1['size']['bytes'] < 1024 * 1024:  # < 1MB
                    try:
                        with open(path1, 'r', encoding='utf-8') as f1, \
                             open(path2, 'r', encoding='utf-8') as f2:
                            
                            lines1 = f1.readlines()
                            lines2 = f2.readlines()
                            
                            if len(lines1) != len(lines2):
                                result['differences'].append(f"Número de líneas diferente: {len(lines1)} vs {len(lines2)}")
                            else:
                                for i, (line1, line2) in enumerate(zip(lines1, lines2)):
                                    if line1 != line2:
                                        result['differences'].append(f"Diferencia en línea {i+1}")
                                        break
                    except Exception:
                        result['differences'].append("No se pudo comparar contenido texto")
        
        result['identical'] = len(result['differences']) == 0
        
        return result
    
    # ============================================================================
    # FUNCIÓN 17: Resumen de directorio
    # ============================================================================
    def get_directory_files_summary(self, 
                                    directory: Union[str, Path],
                                    group_by: str = "extension") -> Dict[str, Any]:
        """
        Obtiene resumen de archivos en directorio.
        
        Args:
            directory: Directorio a analizar
            group_by: Criterio de agrupamiento ("extension", "size_range", "month")
            
        Returns:
            Diccionario con resumen de archivos
        """
        dir_path = self._resolve_path(directory, must_exist=True)
        
        if not dir_path.is_dir():
            return {"error": "No es un directorio válido"}
        
        files = []
        total_size = 0
        extensions = {}
        size_ranges = {
            'tiny': 0,      # < 1KB
            'small': 0,     # 1KB - 1MB
            'medium': 0,    # 1MB - 10MB
            'large': 0,     # 10MB - 100MB
            'huge': 0       # > 100MB
        }
        
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                try:
                    size = file_path.stat().st_size
                    total_size += size
                    
                    files.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'size': size,
                        'extension': file_path.suffix.lower(),
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                    })
                    
                    # Contar por extensión
                    ext = file_path.suffix.lower()
                    if ext:
                        extensions[ext] = extensions.get(ext, 0) + 1
                    else:
                        extensions['sin_extension'] = extensions.get('sin_extension', 0) + 1
                    
                    # Contar por rango de tamaño
                    if size < 1024:
                        size_ranges['tiny'] += 1
                    elif size < 1024 * 1024:
                        size_ranges['small'] += 1
                    elif size < 10 * 1024 * 1024:
                        size_ranges['medium'] += 1
                    elif size < 100 * 1024 * 1024:
                        size_ranges['large'] += 1
                    else:
                        size_ranges['huge'] += 1
                        
                except (OSError, PermissionError):
                    continue
        
        # Ordenar extensiones por frecuencia
        sorted_extensions = dict(sorted(extensions.items(), key=lambda x: x[1], reverse=True))
        
        summary = {
            'directory': str(dir_path),
            'total_files': len(files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'extensions': sorted_extensions,
            'size_ranges': size_ranges,
            'oldest_file': min(files, key=lambda x: x['modified'])['name'] if files else None,
            'newest_file': max(files, key=lambda x: x['modified'])['name'] if files else None,
            'largest_file': max(files, key=lambda x: x['size'])['name'] if files else None,
            'smallest_file': min(files, key=lambda x: x['size'])['name'] if files else None
        }
        
        # Agrupamiento adicional según criterio
        if group_by == "month" and files:
            by_month = {}
            for file_info in files:
                month_key = file_info['modified'].strftime('%Y-%m')
                by_month[month_key] = by_month.get(month_key, 0) + 1
            summary['grouped_by_month'] = dict(sorted(by_month.items()))
        
        return summary
    
    # ============================================================================
    # FUNCIÓN 18: Renombrar por lotes
    # ============================================================================
    def batch_rename(self, 
                     directory: Union[str, Path], 
                     pattern: str,
                     replacement: str, 
                     dry_run: bool = True) -> List[Dict[str, str]]:
        """
        Renombra archivos por lotes con patrón.
        
        Args:
            directory: Directorio con archivos a renombrar
            pattern: Patrón regex a buscar en nombres
            replacement: Texto de reemplazo
            dry_run: Si True, solo muestra cambios sin aplicarlos
            
        Returns:
            Lista de cambios realizados (o que se realizarían)
        """
        dir_path = self._resolve_path(directory, must_exist=True)
        
        if not dir_path.is_dir():
            return []
        
        changes = []
        
        for file_path in dir_path.iterdir():
            if file_path.is_file():
                old_name = file_path.name
                
                # Aplicar regex al nombre
                try:
                    new_name = re.sub(pattern, replacement, old_name)
                except re.error:
                    new_name = old_name
                
                # Limpiar nuevo nombre
                new_name = self.clean_filename(new_name)
                
                if new_name != old_name:
                    new_path = file_path.parent / new_name
                    
                    change_info = {
                        'old_name': old_name,
                        'new_name': new_name,
                        'old_path': str(file_path),
                        'new_path': str(new_path)
                    }
                    
                    if not dry_run:
                        # Verificar que no haya conflicto
                        if new_path.exists():
                            new_path = self.generate_unique_filename(new_path)
                            change_info['new_name'] = new_path.name
                            change_info['new_path'] = str(new_path)
                        
                        try:
                            file_path.rename(new_path)
                            change_info['applied'] = True
                        except Exception as e:
                            change_info['applied'] = False
                            change_info['error'] = str(e)
                    else:
                        change_info['applied'] = False
                        change_info['dry_run'] = True
                    
                    changes.append(change_info)
        
        return changes
    
    # ============================================================================
    # FUNCIÓN 19: Calcular hash
    # ============================================================================
    def calculate_hash(self, 
                       file_path: Union[str, Path],
                       algorithm: str = "md5") -> str:
        """
        Calcula hash criptográfico de archivo.
        
        Args:
            file_path: Ruta del archivo
            algorithm: Algoritmo a usar ("md5", "sha1", "sha256")
            
        Returns:
            String hash hexadecimal
        """
        path_obj = self._resolve_path(file_path)
        
        if not path_obj.exists() or not path_obj.is_file():
            return "FILE_NOT_FOUND"
        
        # Seleccionar algoritmo
        if algorithm == "md5":
            hash_obj = hashlib.md5()
        elif algorithm == "sha1":
            hash_obj = hashlib.sha1()
        elif algorithm == "sha256":
            hash_obj = hashlib.sha256()
        else:
            raise ValueError(f"Algoritmo no soportado: {algorithm}")
        
        try:
            with open(path_obj, 'rb') as f:
                # Leer en bloques para manejar archivos grandes
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
            
        except (IOError, PermissionError):
            return "READ_ERROR"
    
    # ============================================================================
    # FUNCIÓN 20: Comprimir archivo
    # ============================================================================
    def compress_file(self, 
                      source: Union[str, Path], 
                      destination: Optional[Union[str, Path]] = None,
                      format: str = "zip") -> Path:
        """
        Comprime archivo individual.
        
        Args:
            source: Archivo a comprimir
            destination: Ruta destino (default: misma ruta con extensión .zip)
            format: Formato de compresión ("zip")
            
        Returns:
            Path del archivo comprimido creado
        """
        src_path = self._resolve_path(source, must_exist=True)
        
        if destination is None:
            dest_path = src_path.with_suffix('.zip')
        else:
            dest_path = self._resolve_path(destination)
        
        if format.lower() != "zip":
            raise ValueError(f"Formato no soportado: {format}")
        
        # Crear archivo ZIP
        with zipfile.ZipFile(dest_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(src_path, src_path.name)
        
        return dest_path
    
    # ============================================================================
    # FUNCIÓN 21: Extraer archivo
    # ============================================================================
    def extract_file(self, 
                     archive_path: Union[str, Path],
                     destination: Optional[Union[str, Path]] = None) -> Path:
        """
        Extrae archivo comprimido.
        
        Args:
            archive_path: Archivo comprimido
            destination: Directorio destino (default: mismo directorio)
            
        Returns:
            Path del directorio de extracción
        """
        archive = self._resolve_path(archive_path, must_exist=True)
        
        if destination is None:
            dest_dir = archive.parent / archive.stem
        else:
            dest_dir = self._resolve_path(destination)
        
        # Crear directorio destino
        self._ensure_directory(dest_dir)
        
        # Extraer archivo
        if archive.suffix.lower() == '.zip':
            with zipfile.ZipFile(archive, 'r') as zipf:
                zipf.extractall(dest_dir)
        else:
            raise ValueError(f"Formato de archivo no soportado: {archive.suffix}")
        
        return dest_dir
    
    # ============================================================================
    # FUNCIÓN 22: Monitorear cambios
    # ============================================================================
    def monitor_directory_changes(self, 
                                  directory: Union[str, Path],
                                  callback: Callable,
                                  interval: int = 5) -> None:
        """
        Monitorea cambios en directorio.
        
        Args:
            directory: Directorio a monitorear
            callback: Función a llamar cuando hay cambios
            interval: Intervalo de verificación en segundos
        """
        import time
        
        dir_path = self._resolve_path(directory, must_exist=True)
        
        if not dir_path.is_dir():
            raise ValueError(f"No es un directorio válido: {dir_path}")
        
        # Estado inicial
        last_state = {}
        for item in dir_path.rglob('*'):
            if item.is_file():
                try:
                    stat = item.stat()
                    last_state[str(item)] = {
                        'size': stat.st_size,
                        'mtime': stat.st_mtime
                    }
                except (OSError, PermissionError):
                    continue
        
        print(f"Monitoreando {dir_path} cada {interval} segundos...")
        print("Presiona Ctrl+C para detener.")
        
        try:
            while True:
                time.sleep(interval)
                
                current_state = {}
                changes = []
                
                # Escanear directorio actual
                for item in dir_path.rglob('*'):
                    if item.is_file():
                        try:
                            stat = item.stat()
                            item_path = str(item)
                            current_state[item_path] = {
                                'size': stat.st_size,
                                'mtime': stat.st_mtime
                            }
                            
                            # Detectar cambios
                            if item_path not in last_state:
                                changes.append(('created', item_path))
                            elif (current_state[item_path]['size'] != last_state[item_path]['size'] or
                                  current_state[item_path]['mtime'] != last_state[item_path]['mtime']):
                                changes.append(('modified', item_path))
                                
                        except (OSError, PermissionError):
                            continue
                
                # Detectar eliminaciones
                for old_path in last_state:
                    if old_path not in current_state:
                        changes.append(('deleted', old_path))
                
                # Llamar callback si hay cambios
                if changes:
                    callback(changes, dir_path)
                
                # Actualizar estado
                last_state = current_state.copy()
                
        except KeyboardInterrupt:
            print("\nMonitoreo detenido.")
    
    # ============================================================================
    # FUNCIÓN 23: Crear estructura anidada
    # ============================================================================
    def create_nested_structure(self, structure: Dict, base_dir: Optional[Path] = None) -> Dict[str, Path]:
        """
        Crea estructura anidada de directorios desde diccionario.
        
        Args:
            structure: Diccionario con estructura {name: {path: "...", children: {...}}}
            base_dir: Directorio base (default: self.base_dir)
            
        Returns:
            Diccionario con todas las rutas creadas
        """
        if base_dir is None:
            base_dir = self.base_dir
        
        created_paths = {}
        
        def create_recursive(config: Dict, current_path: Path, prefix: str = ''):
            for key, value in config.items():
                if isinstance(value, dict) and 'path' in value:
                    # Crear directorio
                    dir_path = current_path / value['path']
                    dir_path = self._ensure_directory(dir_path)
                    
                    # Guardar ruta
                    full_key = f"{prefix}.{key}" if prefix else key
                    created_paths[full_key] = dir_path
                    
                    # Crear subdirectorios
                    if 'children' in value:
                        create_recursive(value['children'], dir_path, full_key)
        
        create_recursive(structure, base_dir)
        return created_paths
    
    # ============================================================================
    # FUNCIÓN 24: Detectar encoding
    # ============================================================================
    def get_file_encoding(self, file_path: Path) -> str:
        """
        Detecta encoding de archivo de texto.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            String con encoding detectado
        """
        try:
            # Intentar importar chardet dinámicamente
            try:
                import chardet
            except ImportError:
                # Si chardet no está disponible, usar método simple
                return self._simple_encoding_detection(file_path)
            
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Leer primeros 10KB
            
            result = chardet.detect(raw_data)
            return result.get('encoding', 'utf-8')
        except Exception:
            return 'utf-8'
    
    # ============================================================================
    # FUNCIÓN 25: Verificar archivo binario
    # ============================================================================
    def is_binary_file(self, file_path: Path) -> bool:
        """
        Verifica si un archivo es binario.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            True si es binario, False si es texto
        """
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                # Archivo binario si contiene bytes nulos
                return b'\x00' in chunk
        except Exception:
            return True
    
    # ============================================================================
    # FUNCIÓN 26: Obtener tipo MIME
    # ============================================================================
    def get_mime_type(self, file_path: Path) -> str:
        """
        Obtiene tipo MIME de archivo.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            String con tipo MIME
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'
    
    # ============================================================================
    # MÉTODOS AUXILIARES INTERNOS (reemplazan a PathManager)
    # ============================================================================
    
    def _resolve_path(self, path: Union[str, Path], must_exist: bool = False) -> Path:
        """
        Resuelve y normaliza una ruta con expansión de variables.
        
        Args:
            path: Ruta a resolver (string o Path)
            must_exist: Si True, valida que la ruta exista
            
        Returns:
            Path resuelto y normalizado
            
        Raises:
            FileNotFoundError: Si must_exist=True y la ruta no existe
        """
        if isinstance(path, str):
            # Expandir variables y usuario
            expanded = self._expand_path_variables(path)
            path_obj = Path(expanded)
        else:
            path_obj = path
        
        # Resolver a ruta absoluta
        try:
            resolved = path_obj.expanduser().resolve()
        except RuntimeError:
            # Si hay symlinks circulares, usar absolute()
            resolved = path_obj.expanduser().absolute()
        
        # Validar existencia si es requerido
        if must_exist and not resolved.exists():
            raise FileNotFoundError(f"Ruta no encontrada: {resolved}")
        
        return resolved
    
    def _ensure_directory(self, dir_path: Union[str, Path]) -> Path:
        """
        Asegura que un directorio existe, creándolo si es necesario.
        
        Args:
            dir_path: Ruta del directorio
            
        Returns:
            Path del directorio (existente o recién creado)
        """
        resolved = self._resolve_path(dir_path)
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved
    
    def _is_within_base(self, target_path: Union[str, Path]) -> bool:
        """
        Verifica que una ruta esté dentro del directorio base seguro.
        
        Args:
            target_path: Ruta a verificar
            
        Returns:
            True si está dentro del directorio base, False en caso contrario
        """
        try:
            target = self._resolve_path(target_path)
            base = self.base_dir.resolve()
            
            # Comparar paths resueltos
            try:
                target.relative_to(base)
                return True
            except ValueError:
                return False
        except Exception:
            return False
    
    def _make_unique_path(self, base_path: Union[str, Path]) -> Path:
        """
        Genera una ruta única que no existe en el sistema.
        
        Args:
            base_path: Ruta base deseada
            
        Returns:
            Path único que no existe
        """
        resolved = self._resolve_path(base_path)
        
        if not resolved.exists():
            return resolved
        
        # Intentar con números incrementales
        counter = 1
        while True:
            parent = resolved.parent
            stem = resolved.stem
            suffix = resolved.suffix
            
            # Patrón: nombre_1.ext, nombre_2.ext, etc.
            unique_name = f"{stem}_{counter}{suffix}"
            unique_path = parent / unique_name
            
            if not unique_path.exists():
                return unique_path
            
            counter += 1
            
            # Prevenir bucle infinito
            if counter > 1000:
                # Usar timestamp como último recurso
                import time
                timestamp = int(time.time() * 1000)
                unique_name = f"{stem}_{timestamp}{suffix}"
                return parent / unique_name
    
    def _expand_path_variables(self, path_str: str) -> str:
        """
        Expande variables de entorno y usuario en una ruta.
        
        Args:
            path_str: Cadena de ruta con posibles variables
            
        Returns:
            String con variables expandidas
        """
        # Expandir usuario (~)
        expanded = os.path.expanduser(path_str)
        
        # Expandir variables de entorno
        expanded = os.path.expandvars(expanded)
        
        return expanded
    
    def _is_text_file(self, file_path: Path) -> bool:
        """
        Determina si un archivo es de texto basado en contenido.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            True si es archivo de texto, False en caso contrario
        """
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                # Archivo de texto si no hay bytes nulos y es principalmente ASCII
                return b'\x00' not in chunk and chunk.decode('utf-8', errors='ignore').isprintable()
        except:
            return False
    
    def _simple_encoding_detection(self, file_path: Path) -> str:
        """
        Detección simple de encoding sin dependencias externas.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Encoding detectado
        """
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(1024)
                return encoding
            except UnicodeDecodeError:
                continue
        
        return 'utf-8'
    
    def _setup_default_workspace(self):
        """Configura estructura por defecto de directorios."""
        for dir_path in self.workspace_structure.values():
            self._ensure_directory(dir_path)
    
    # ============================================================================
    # FUNCIONES PÚBLICAS DE GESTIÓN DE RUTAS (similares a PathManager)
    # ============================================================================
    
    def setup_workspace(self, dir_structure: Dict[str, Union[str, Path]]) -> Dict[str, Path]:
        """
        Configura estructura completa de directorios de trabajo.
        
        Args:
            dir_structure: Diccionario de mapa de rutas {nombre: ruta}.
                           Puede contener rutas relativas o absolutas.
                           ES OBLIGATORIO.
                           
        Returns:
            Diccionario con tipos de directorio confirmados.
            
        Raises:
            ValueError: Si dir_structure es None o vacío.
        """
        if not dir_structure:
            raise ValueError("Directory structure dictionary is required for setup_workspace. (Explicit is better than implicit)")
        
        self.workspace_structure = {}
        
        for name, path_val in dir_structure.items():
            if name == 'root': continue  # Skip root definition itself

            # Normalizar a Path
            if isinstance(path_val, str):
                target_path = Path(path_val)
            else:
                 target_path = path_val

            # Resolver ruta relativa
            if not target_path.is_absolute():
                target_path = self.base_dir / target_path
            
            # Crear y registrar
            self._ensure_directory(target_path)
            self.workspace_structure[name] = target_path
            
        return self.workspace_structure.copy()
    
    def get_path_info(self, path: Union[str, Path]) -> Dict[str, Any]:
        """
        Obtiene información detallada de una ruta.
        
        Args:
            path: Ruta a analizar
            
        Returns:
            Diccionario con información de la ruta
        """
        try:
            resolved = self._resolve_path(path)
            stat = resolved.stat() if resolved.exists() else None
            
            info = {
                'original': str(path),
                'resolved': str(resolved),
                'absolute': str(resolved.absolute()),
                'exists': resolved.exists(),
                'is_file': resolved.is_file() if resolved.exists() else False,
                'is_dir': resolved.is_dir() if resolved.exists() else False,
                'is_symlink': resolved.is_symlink() if resolved.exists() else False,
                'parent': str(resolved.parent),
                'name': resolved.name,
                'stem': resolved.stem if resolved.exists() else '',
                'suffix': resolved.suffix if resolved.exists() else '',
                'relative_to_base': self._get_relative_to_base(resolved) if self._is_within_base(resolved) else None,
                'within_base': self._is_within_base(resolved),
            }
            
            if stat:
                info.update({
                    'size_bytes': stat.st_size,
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime,
                    'accessed': stat.st_atime,
                    'permissions': oct(stat.st_mode)[-3:],
                })
            
            return info
            
        except Exception as e:
            return {
                'error': str(e),
                'original': str(path),
                'exists': False
            }
    
    def _get_relative_to_base(self, path: Union[str, Path]) -> str:
        """
        Obtiene la ruta relativa respecto al directorio base.
        
        Args:
            path: Ruta para calcular la relativa
            
        Returns:
            Ruta relativa como string
            
        Raises:
            ValueError: Si la ruta no está dentro del directorio base
        """
        resolved_path = self._resolve_path(path)
        
        if not self._is_within_base(resolved_path):
            raise ValueError(f"Ruta fuera del directorio base: {resolved_path}")
        
        try:
            return str(resolved_path.relative_to(self.base_dir))
        except ValueError:
            # Fallback: calcular manualmente
            base_str = str(self.base_dir)
            path_str = str(resolved_path)
            
            if path_str.startswith(base_str):
                relative = path_str[len(base_str):].lstrip('/\\')
                return relative
            else:
                raise ValueError(f"No se pudo calcular ruta relativa")
    
    def _get_default_structure(self) -> Dict[str, str]:
        """Retorna la estructura por defecto de directorios."""
        return {
            'input': 'Input',
            'output': 'Output',
            'backups': 'Output/Backups',
            'processed': 'Output/Processed',
            'reports': 'Output/Reports',
            'temp': 'Temp',
            'logs': 'Logs',
            'data': 'Data',
            'config': 'Config',
            'exports': 'Exports',
        }
    
    def get_workspace_path(self, dir_type: str) -> Optional[Path]:
        """Obtiene ruta de un directorio del workspace por tipo."""
        return self.workspace_structure.get(dir_type)


# ============================================================================
# FUNCIONES AUXILIARES DEL MÓDULO (para uso externo)
# ============================================================================

def expand_path_variables(path_str: str) -> str:
    """
    Expande variables de entorno y usuario en una ruta.
    
    Args:
        path_str: Cadena de ruta con posibles variables
        
    Returns:
        String con variables expandidas
    """
    # Expandir usuario (~)
    expanded = os.path.expanduser(path_str)
    
    # Expandir variables de entorno
    expanded = os.path.expandvars(expanded)
    
    return expanded


def is_valid_path_syntax(path_str: str) -> bool:
    """
    Verifica si una cadena tiene sintaxis de ruta válida.
    
    Args:
        path_str: Cadena a validar
        
    Returns:
        True si la sintaxis es válida, False en caso contrario
    """
    if not path_str or not isinstance(path_str, str):
        return False
    
    # Caracteres prohibidos en nombres de archivo/ruta (Windows)
    invalid_chars = r'[<>:"|?\*\x00-\x1F]'
    
    if re.search(invalid_chars, path_str):
        return False
    
    # Verificar componentes vacíos
    parts = path_str.replace('\\', '/').split('/')
    for part in parts:
        if part in ('', '.', '..'):
            continue
        if part.endswith(' ') or part.endswith('.'):
            return False  # Windows no permite espacios o puntos al final
    
    return True


def safe_path_join(base: Union[str, Path], *parts: str) -> Path:
    """
    Une rutas de forma segura previniendo path traversal.
    
    Args:
        base: Directorio base seguro
        *parts: Partes de ruta a unir
        
    Returns:
        Path unido dentro del directorio base
    """
    if isinstance(base, str):
        base_path = Path(base).resolve()
    else:
        base_path = base.resolve()
    
    # Comenzar desde el directorio base
    current = base_path
    
    for part in parts:
        # Limpiar cada parte
        clean_part = part.strip().replace('\\', '/').strip('/')
        
        # Saltar partes vacías o puntos
        if not clean_part or clean_part == '.':
            continue
        
        # Prevenir path traversal
        if clean_part == '..':
            # Solo permitir si no salimos del directorio base
            if current.parent != current and current.parent != base_path.parent:
                current = current.parent
            continue
        
        # Añadir parte a la ruta actual
        current = current / clean_part
    
    return current.resolve()


# ============================================================================
# FUNCIÓN PRINCIPAL DE PRUEBA
# ============================================================================
def _test_file_handler() -> None:
    """Función de prueba para el módulo file_handler"""
    print("=" * 60)
    print("PRUEBA DE FILE HANDLER INDEPENDIENTE")
    print("=" * 60)
    
    # Crear FileSystemManager
    fm = FileSystemManager()
    
    print(f"\n1. FileSystemManager inicializado")
    print(f"   Directorio base: {fm.base_dir}")
    
    # Probar búsqueda de archivos
    print("\n2. Probando búsqueda de archivos Excel:")
    excel_files = fm.find_excel_files(fm.base_dir, recursive=False)
    print(f"   Archivos Excel encontrados: {len(excel_files)}")
    for i, file_path in enumerate(excel_files[:3], 1):  # Mostrar primeros 3
        print(f"   {i}. {file_path.name}")
    if len(excel_files) > 3:
        print(f"   ... y {len(excel_files) - 3} más")
    
    # Probar limpieza de nombres
    print("\n3. Probando limpieza de nombres de archivo:")
    test_names = [
        "Documento con espacios y/caracteres?extraños.xlsx",
        "normal-file.pdf",
        "  con espacios al inicio y final  .docx",
        "archivo<con>caracteres>inválidos.txt"
    ]
    
    for name in test_names:
        cleaned = fm.clean_filename(name)
        print(f"   '{name}'")
        print(f"     → '{cleaned}'")
    
    # Probar obtención de información
    print("\n4. Probando obtención de información de archivo:")
    if excel_files:
        sample_file = excel_files[0]
        info = fm.get_file_info(sample_file)
        
        print(f"   Archivo: {sample_file.name}")
        print(f"   Tamaño: {info['size']['mb']:.2f} MB")
        print(f"   Modificado: {info['timestamps']['modified'].strftime('%Y-%m-%d %H:%M')}")
        print(f"   Tipo MIME: {info['type_info']['mime_type']}")
        if 'md5' in info['hash']:
            print(f"   Hash MD5: {info['hash']['md5'][:16]}...")
    else:
        print("   No hay archivos Excel para probar")
    
    # Probar validación de integridad
    print("\n5. Probando validación de integridad:")
    test_file = fm.base_dir / "test_integrity.txt"
    
    # Crear archivo de prueba
    try:
        with open(test_file, 'w') as f:
            f.write("Contenido de prueba para validación\n")
        
        validation = fm.validate_file_integrity(test_file)
        print(f"   Archivo: {test_file.name}")
        print(f"   Existe: {'✓' if validation['exists'] else '✗'}")
        print(f"   Es archivo: {'✓' if validation['is_file'] else '✗'}")
        print(f"   Legible: {'✓' if validation['readable'] else '✗'}")
        print(f"   Puntuación integridad: {validation['integrity_score']}")
        
        # Limpiar
        test_file.unlink(missing_ok=True)
    except Exception as e:
        print(f"   Error en prueba: {e}")
    
    # Probar funciones auxiliares
    print("\n6. Probando funciones auxiliares:")
    test_path = "~/test/${USER}/file.txt"
    expanded = expand_path_variables(test_path)
    print(f"   Expandir variables: '{test_path}' → '{expanded}'")
    
    invalid_path = "file<invalid>.txt"
    valid_path = "normal_file.txt"
    print(f"   Validar sintaxis: '{invalid_path}' → {is_valid_path_syntax(invalid_path)}")
    print(f"   Validar sintaxis: '{valid_path}' → {is_valid_path_syntax(valid_path)}")
    
    print("\n" + "=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)


if __name__ == "__main__":
    _test_file_handler()