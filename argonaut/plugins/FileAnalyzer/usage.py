from argonaut import Argonaut
from argonaut.exceptions import ArgonautError
from argonaut.plugins import PluginError
from argonaut.logging import LogLevel

def main():
    parser = Argonaut(description="File Analyzer Application")
    
    # Add the global options before loading plugins
    parser.add_global_argument('--verbose', action='store_true', help="Enable verbose output")
    parser.add_global_argument('--quiet', action='store_true', help="Run in quiet mode (minimal output)")
    
    try:
        # Load the FileAnalyzer plugin
        parser.load_plugin("file_analyzer_plugin")
        
        # Parse arguments
        args = parser.parse()
        
        if args.get('verbose'):
            parser.logger.set_level(LogLevel.DEBUG)
        elif args.get('quiet'):
            parser.logger.set_level(LogLevel.ERROR)
        
        # List loaded plugins
        if not args.get('quiet'):
            print(parser.colored_output.custom_color("Loaded plugins:", "green"))
            for plugin in parser.list_plugins():
                print(parser.colored_output.custom_color(f"- {plugin['name']} v{plugin['version']} by {plugin['author']}", "yellow"))
                print(parser.colored_output.custom_color(f"  {plugin['description']}", "blue"))
                print(parser.colored_output.custom_color(f"  Website: {plugin['website']}", "blue"))
                if 'tags' in plugin and plugin['tags']:
                    print(parser.colored_output.custom_color(f"  Tags: {', '.join(plugin['tags'])}", "blue"))
        
        # Execute the plugin if needed
        if args.get('subcommand') == 'analyze':
            try:
                result = parser.execute_plugin("file_analyzer", args)
                print(result)
            except PluginError as e:
                print(parser.colored_output.red(f"Plugin error: {str(e)}"))
        else:
            print(parser.generate_help())
        
    except ArgonautError as e:
        print(parser.colored_output.custom_color(f"Error: {str(e)}", "red"))
    finally:
        # Unload the plugin when done
        parser.unload_plugin("file_analyzer")

if __name__ == "__main__":
    main()