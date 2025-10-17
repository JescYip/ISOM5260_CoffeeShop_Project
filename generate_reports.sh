#!/bin/bash

# Coffee Shop Report Generation Script
# ====================================
# This script generates comprehensive reports from the coffee shop database
# and compiles them into a LaTeX document.

set -e  # Exit on any error

# Configuration
DB_PATH="coffee_shop.db"
OUTPUT_DIR="reports"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python dependencies
check_python_deps() {
    print_status "Checking Python dependencies..."
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check if required packages are installed
    python3 -c "import pandas, matplotlib, seaborn, yaml" 2>/dev/null || {
        print_warning "Some Python packages are missing. Installing..."
        pip3 install -r requirements_reports.txt
    }
    
    print_success "Python dependencies are ready"
}

# Function to check LaTeX installation
check_latex() {
    print_status "Checking LaTeX installation..."
    
    if ! command_exists pdflatex; then
        print_warning "LaTeX is not installed. PDF generation will be skipped."
        print_warning "Install LaTeX with: sudo apt-get install texlive-latex-base texlive-latex-extra"
        return 1
    fi
    
    print_success "LaTeX is available"
    return 0
}

# Function to check database
check_database() {
    print_status "Checking database..."
    
    if [ ! -f "$DB_PATH" ]; then
        print_error "Database file not found: $DB_PATH"
        print_error "Please ensure the database exists and the path is correct"
        exit 1
    fi
    
    # Check if database has data
    if ! python3 -c "
import sqlite3
conn = sqlite3.connect('$DB_PATH')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM CYEAE_ORDERS')
count = cursor.fetchone()[0]
conn.close()
if count == 0:
    exit(1)
" 2>/dev/null; then
        print_warning "Database appears to be empty or has no order data"
        print_warning "Reports may not contain meaningful data"
    fi
    
    print_success "Database is accessible"
}

# Function to generate reports
generate_reports() {
    print_status "Generating reports..."
    
    cd "$SCRIPT_DIR"
    
    # Run the Python report generator
    python3 report_generator.py --db "$DB_PATH" --output-dir "$OUTPUT_DIR"
    
    if [ $? -eq 0 ]; then
        print_success "Reports generated successfully"
    else
        print_error "Report generation failed"
        exit 1
    fi
}

# Function to compile LaTeX document
compile_latex() {
    if ! check_latex; then
        return 1
    fi
    
    print_status "Compiling LaTeX document..."
    
    cd "$SCRIPT_DIR/$OUTPUT_DIR/latex"
    
    # Run pdflatex twice for proper cross-references
    pdflatex -interaction=nonstopmode coffee_shop_report.tex > /dev/null 2>&1
    pdflatex -interaction=nonstopmode coffee_shop_report.tex > /dev/null 2>&1
    
    if [ -f "coffee_shop_report.pdf" ]; then
        print_success "PDF report generated: $OUTPUT_DIR/latex/coffee_shop_report.pdf"
        return 0
    else
        print_error "PDF generation failed"
        return 1
    fi
}

# Function to open the generated report
open_report() {
    local pdf_path="$SCRIPT_DIR/$OUTPUT_DIR/latex/coffee_shop_report.pdf"
    
    if [ -f "$pdf_path" ]; then
        print_status "Opening generated report..."
        
        if command_exists xdg-open; then
            xdg-open "$pdf_path"
        elif command_exists open; then
            open "$pdf_path"
        else
            print_warning "Cannot automatically open PDF. Please open manually:"
            print_warning "$pdf_path"
        fi
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -d, --db PATH       Database file path (default: coffee_shop.db)"
    echo "  -o, --output DIR    Output directory (default: reports)"
    echo "  --no-pdf           Skip PDF generation"
    echo "  --no-open          Don't open the generated PDF"
    echo ""
    echo "Examples:"
    echo "  $0                          # Generate reports with default settings"
    echo "  $0 -d my_db.db -o my_reports # Use custom database and output directory"
    echo "  $0 --no-pdf                 # Generate charts and data only"
}

# Main function
main() {
    local skip_pdf=false
    local skip_open=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -d|--db)
                DB_PATH="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            --no-pdf)
                skip_pdf=true
                shift
                ;;
            --no-open)
                skip_open=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Print header
    echo "=========================================="
    echo "  Coffee Shop Report Generator"
    echo "=========================================="
    echo "Database: $DB_PATH"
    echo "Output: $OUTPUT_DIR"
    echo "=========================================="
    echo ""
    
    # Run checks and generation
    check_python_deps
    check_database
    generate_reports
    
    # Compile LaTeX if requested
    if [ "$skip_pdf" = false ]; then
        if compile_latex; then
            if [ "$skip_open" = false ]; then
                open_report
            fi
        fi
    fi
    
    # Show summary
    echo ""
    echo "=========================================="
    echo "  Report Generation Complete"
    echo "=========================================="
    echo "Charts: $OUTPUT_DIR/charts/"
    echo "Data: $OUTPUT_DIR/data/"
    echo "LaTeX: $OUTPUT_DIR/latex/"
    
    if [ -f "$SCRIPT_DIR/$OUTPUT_DIR/latex/coffee_shop_report.pdf" ]; then
        echo "PDF: $OUTPUT_DIR/latex/coffee_shop_report.pdf"
    fi
    
    echo "=========================================="
}

# Run main function with all arguments
main "$@"
