  #ifndef JOJO_H
  #define JOJO_H
  #include <sys/types.h>
  #include <sys/stat.h>
  #include <unistd.h>
  #include <stdio.h>
  #include <stdlib.h>
  #include <errno.h>
  #include <string.h>
  #include <fcntl.h>
  #include <ctype.h>
  #include <stdint.h>
  #include <dlfcn.h>
  #include <dirent.h>
  #include <signal.h>
  #include <limits.h>
  #include <stdarg.h>
  typedef enum { false, true } bool;
  typedef intptr_t cell;
  typedef void (* primitive_t)();
    extern void report(char* format, ...);
    extern void report_in_red(char* format, ...);
    extern void report_in_green(char* format, ...);
  extern void p_debug();
    struct jotable_entry {
      char *key;
      struct jotable_entry *tag;
      cell data;
    };

    typedef struct jotable_entry* jo_t;

    // prime table size
    //   1000003   about 976 k
    //   1000033
    //   1000333
    //   100003    about 97 k
    //   100333
    //   997
    #define JOTABLE_SIZE 100003
    struct jotable_entry jotable[JOTABLE_SIZE];

    // thus (jotable + index) is jo
    extern jo_t str2jo(char* str);
    extern char* jo2str(jo_t jo);
    extern jo_t EMPTY_JO;

    extern jo_t TAG_PRIM;
    extern jo_t TAG_JOJO;
    extern jo_t TAG_CLOSURE;
    extern jo_t TAG_ADDRESS;
    extern jo_t TAG_CLASS;

    extern jo_t TAG_LOCAL_ENV;

    extern jo_t TAG_BOOL;
    extern jo_t TAG_INT;
    extern jo_t TAG_BYTE;
    extern jo_t TAG_STRING;
    extern jo_t TAG_ARRAY;
    extern jo_t TAG_JO;

    extern jo_t TAG_MARK;

    extern jo_t TAG_UNINITIALISED_FIELD_PLACE_HOLDER;

    extern jo_t TAG_FILE;
    extern jo_t TAG_SOCKET;
    extern jo_t TAG_INPUT_STACK;

    extern jo_t TAG_DATA_PREDICATE;
    extern jo_t TAG_DATA_CONSTRUCTOR;

    extern jo_t TAG_GENE;

    extern jo_t ROUND_BAR;
    extern jo_t ROUND_KET;
    extern jo_t SQUARE_BAR;
    extern jo_t SQUARE_KET;
    extern jo_t FLOWER_BAR;
    extern jo_t FLOWER_KET;
    extern jo_t DOUBLEQUOTE;
    extern jo_t SINGLEQUOTE;
    extern jo_t BACKQUOTE;
    extern jo_t COMMA;

    extern jo_t JO_INS_LIT;

    extern jo_t JO_INS_LOCAL;
    extern jo_t JO_INS_SET_LOCAL;

    extern jo_t JO_INS_DYNAMIC_LOCAL;
    extern jo_t JO_INS_SET_DYNAMIC_LOCAL;

    extern jo_t JO_INS_FIELD;
    extern jo_t JO_INS_SET_FIELD;

    extern jo_t JO_INS_JMP;
    extern jo_t JO_INS_JZ;

    extern jo_t JO_NULL;
    extern jo_t JO_THEN;
    extern jo_t JO_ELSE;

    extern jo_t JO_APPLY;
    extern jo_t JO_EXE;
    extern jo_t JO_END;
    extern jo_t JO_RECUR;
    extern jo_t JO_CLOSURE;
    extern jo_t JO_CURRENT_LOCAL_ENV;
    extern jo_t name_record[];
    extern cell name_record_counter;
    extern bool core_flag;
    extern void bind_name(jo_t name,
                          jo_t tag,
                          cell data);
    extern void rebind_name(jo_t name,
                            jo_t tag,
                            cell data);
      // caller free
      extern jo_t* generate_jo_array(char*ss[]);
      #define J0 (char*[]){0}
      #define J(...) generate_jo_array((char*[]){__VA_ARGS__, 0})
    struct stack_link {
      cell* stack;
      struct stack_link* link;
    };
    struct stack {
      char* name;
      cell pointer;
      cell* stack;
      struct stack_link* link;
    };

    #define STACK_BLOCK_SIZE 1024
    extern struct stack* new_stack(char* name);
    extern void stack_free(struct stack* stack);
    extern bool stack_empty_p(struct stack* stack);
    extern cell stack_length(struct stack* stack);
    extern cell pop(struct stack* stack);
    extern cell tos(struct stack* stack);
    extern void drop(struct stack* stack);
    extern void push(struct stack* stack, cell data);
    extern cell stack_peek(struct stack* stack, cell index);
    extern cell stack_ref(struct stack* stack, cell index);
    typedef enum {
      INPUT_STACK_REGULAR_FILE,
      INPUT_STACK_STRING,
      INPUT_STACK_TERMINAL,
    } input_stack_type;
    struct input_stack_link {
      char* stack;
      cell end_pointer;
      struct input_stack_link* link;
    };
    struct input_stack {
      cell pointer;
      cell end_pointer;
      char* stack;
      struct input_stack_link* link;
      input_stack_type type;
      union {
        int   file;
        char* string;
        // int   terminal;
      };
      cell string_pointer;
    };

    #define INPUT_STACK_BLOCK_SIZE (4 * 1024)
    extern struct input_stack* new_input_stack(input_stack_type input_stack_type);
    extern struct input_stack* file_input_stack(int file);
    extern struct input_stack* string_input_stack(char* string);
    extern struct input_stack* terminal_input_stack();
    extern void input_stack_free(struct input_stack* input_stack);
    extern bool input_stack_empty_p(struct input_stack* input_stack);
    extern char input_stack_pop(struct input_stack* input_stack);
    extern char input_stack_tos(struct input_stack* input_stack);
    extern void input_stack_drop(struct input_stack* input_stack);
    extern void input_stack_push(struct input_stack* input_stack, char byte);
    typedef enum {
      OUTPUT_STACK_REGULAR_FILE,
      OUTPUT_STACK_STRING,
      OUTPUT_STACK_TERMINAL,
    } output_stack_type;
    struct output_stack_link {
      char* stack;
      struct output_stack_link* link;
    };
    struct output_stack {
      cell pointer;
      char* stack;
      struct output_stack_link* link;
      output_stack_type type;
      union {
        int   file; // with cache
        // char* string;
        //   generate string
        //   instead of output to pre-allocated buffer
        // int   terminal; // no cache
      };
      cell string_pointer;
    };

    #define OUTPUT_STACK_BLOCK_SIZE (4 * 1024)
    extern struct output_stack* new_output_stack(output_stack_type output_stack_type);
    extern struct output_stack* file_output_stack(int file);
    extern struct output_stack* string_output_stack();
    extern struct output_stack* terminal_output_stack();
    extern void output_stack_free(struct output_stack* output_stack);
    extern void file_output_stack_flush(struct output_stack* output_stack);
    extern cell string_output_stack_length(struct output_stack* output_stack);

    extern char* string_output_stack_collect(struct output_stack* output_stack);
    extern bool output_stack_empty_p(struct output_stack* output_stack);
    extern char output_stack_pop(struct output_stack* output_stack);
    extern char output_stack_tos(struct output_stack* output_stack);
    extern void output_stack_drop(struct output_stack* output_stack);
    extern void output_stack_push(struct output_stack* output_stack, char b);
    struct dp {
      jo_t t;
      cell d;
    };

    extern struct stack* ds;

    extern struct dp ds_pop();

    extern void ds_drop();

    extern struct dp ds_tos();

    extern bool ds_empty_p();

    extern void ds_push(jo_t tag, cell data);

    extern jo_t ds_peek_tag(cell index);

    extern cell ds_peek_data(cell index);

    extern struct dp ds_ref(cell index);

    extern cell ds_length();
    struct local {
      jo_t name;
      cell local_tag;
      cell local_data;
    };

    #define LOCAL_RECORD_SIZE (16 * 1024)
    extern struct local local_record[LOCAL_RECORD_SIZE];
    extern cell current_local_counter;
    struct dynamic_local {
      jo_t name;
      cell dynamic_local_tag;
      cell dynamic_local_data;
    };

    #define DYNAMIC_LOCAL_RECORD_SIZE (4 * 1024)
    extern struct dynamic_local dynamic_local_record[DYNAMIC_LOCAL_RECORD_SIZE];
    extern cell current_dynamic_local_counter;
    struct rp {
      jo_t* j;
      jo_t  t;
      cell  d;
      cell  l;
      cell  y;
    };

    extern struct stack* rs;

    extern struct rp rs_pop();

    extern void rs_drop();

    extern struct rp rs_tos();

    extern bool rs_empty_p();

    extern void rs_push(jo_t* jojo,
                        jo_t tag,
                        cell data,
                        cell local_counter,
                        cell dynamic_local_counter);

    extern cell rs_length();

    extern struct rp rs_ref(cell index);

    extern void rs_inc();
    typedef enum {
      GC_MARK_FREE,
      GC_MARK_USING,
    } gc_mark_t;

    struct gp { // gc point
      gc_mark_t mark;
      struct class* class;
      cell p; // actual data point
    };
    #define GR_SIZE 64 * 1024
    // #define GR_SIZE 1024
    // #define GR_SIZE 3 // for testing

    extern struct gp gr[GR_SIZE];
    extern struct gp* gr_pointer;
    extern bool gr_end_p();
    extern void init_gr();
    typedef enum {
      GC_STATE_MARKING,
      GC_STATE_SWEEPING,
    } gc_state_t;

    typedef void (* gc_actor_t)(gc_state_t, cell);

    struct class {
      jo_t class_name;
      gc_actor_t gc_actor;
      cell fields_number;
      jo_t* fields;
    };
    extern jo_t get_field_tag(cell* fields, cell field_index);

    extern void set_field_tag(cell* fields, cell field_index, jo_t tag);

    extern cell get_field_data(cell* fields, cell field_index);

    extern void set_field_data(cell* fields, cell field_index, cell data);
    // assume exist
    extern jo_t class_index_to_field_name(struct class* class, cell index);
    // assume exist
    extern cell class_field_name_to_index(struct class* class, jo_t field_name);
    extern jo_t get_gp_field_tag(struct gp* gp, cell field_index);

    extern void set_gp_field_tag(struct gp* gp,
                                 cell field_index,
                                 jo_t tag);

    extern cell get_gp_field_data(struct gp* gp, cell field_index);

    extern void set_gp_field_data(struct gp* gp,
                                  cell field_index,
                                  cell data);
    extern struct dp get_field(jo_t class_tag, struct gp* gp, jo_t name);
    extern void ins_get_field();
    extern void ins_set_field();
    extern void mark_one_data(jo_t tag, cell data);
    extern void mark_gr();
    extern void sweep_one_gp(struct gp* gp);
    extern void sweep_gr();
    extern void run_gc();
      extern void gc_ignore(gc_state_t gc_state, cell data);
      extern void gc_free(gc_state_t gc_state, struct gp* gp);
      extern void gc_recur(gc_state_t gc_state, struct gp* gp);
    extern void next_free_record_gp();

    extern struct gp* new_record_gp();
    extern void plus_atom(char* class_name, gc_actor_t gc_actor);
    // argument 'fields' is shared
    extern void plus_data(char* class_name, jo_t* fields);
    extern void plus_prim(char* function_name, primitive_t fun);
    extern void p_tag();
    extern void p_eq_p();
    extern void p_new();
    extern void expose_gc();
    extern struct gp* new_jojo_gp(jo_t* jojo);
    extern cell jojo_length(jo_t* jojo);
    extern void p_new_jojo();
    extern void gc_jojo(gc_state_t gc_state, struct gp* gp);
    extern void expose_jojo();
      struct disp_entry {
        jo_t key;
        jo_t tag;
        cell data;
        struct disp_entry* rest;
      };

      struct disp {
        struct disp_entry* table;
        cell size;
      };
      extern struct disp* new_disp(cell size);
      extern cell disp_hash(struct disp* disp, jo_t key);
      extern void disp_insert_entry(struct disp_entry* disp_entry,
                                    jo_t key,
                                    jo_t tag,
                                    cell data);
      extern void disp_insert(struct disp* disp, jo_t key, jo_t tag, cell data);
      extern struct disp_entry* disp_find_entry(struct disp_entry* disp_entry,
                                                jo_t key);
      extern struct disp_entry* disp_find(struct disp* disp,
                                          jo_t key);
      extern void disp_print_entry(struct disp_entry* disp_entry);
      extern void disp_print(struct disp* disp);
      struct multi_disp_entry {
        jo_t* key;
        jo_t tag;
        cell data;
        struct multi_disp_entry* rest;
      };

      struct multi_disp {
        struct multi_disp_entry* table;
        cell size;
      };
      extern struct multi_disp* new_multi_disp(cell size);
      extern cell multi_disp_hash(struct multi_disp* multi_disp, jo_t* key);
      // argument 'key' is shared
      extern void multi_disp_insert_entry
      (struct multi_disp_entry* multi_disp_entry,
       jo_t* key,
       jo_t tag,
       cell data);
      extern void multi_disp_insert(struct multi_disp* multi_disp,
                                    jo_t* key,
                                    jo_t tag,
                                    cell data);
      extern struct multi_disp_entry*
      multi_disp_find_entry
      (struct multi_disp_entry* multi_disp_entry,
       jo_t* key);
      extern struct multi_disp_entry*
      multi_disp_find(struct multi_disp* multi_disp,
                      jo_t* key);
      extern void multi_disp_print_entry(struct multi_disp_entry* multi_disp_entry);
      extern void multi_disp_print(struct multi_disp* multi_disp);
    struct gene {
      jo_t tag;
      cell data;
      union {
        jo_t disp;
        jo_t* multi_disp;
      };
      cell arity;
    };
    extern void plus_gene(char* function_name,
                          cell arity);
    // argument 'tags' is shared
    extern void plus_disp(char* gene_name,
                          jo_t* tags,
                          char* tag_name,
                          cell data);
    extern void plus_disp_default(char* gene_name,
                                  char* tag_name,
                                  cell data);
    extern void disp_exe(struct gene* gene, jo_t tag);
    extern void multi_disp_exe(struct gene* gene, jo_t* tags);
    extern void p_gene_exe();
    extern void p_prim_exe();
    extern void p_jojo_exe();
    extern void p_data_predicate_exe();
    extern void p_default_exe();
    extern void expose_gene();
    extern void jo_apply(jo_t jo);
    extern void eval_one_step();
    extern void eval();
    extern void p_end();
    extern void p_bye();
    extern void p_nop();
    extern void expose_ending();
    extern void p_drop();
    extern void p_dup();
    extern void p_over();
    extern void p_tuck();
    extern void p_swap();
    extern void expose_stack();
    extern struct stack* reading_stack; // of input_stack
    extern struct stack* writing_stack; // of output_stack
    extern void p_reading_stack_push();
    extern void p_reading_stack_tos();
    extern void p_reading_stack_pop();
    extern void p_reading_stack_drop();
    extern void p_terminal_input_stack();
    extern void p_input_stack_free();
    extern void p_input_stack_empty_p();
    extern bool has_byte_p();
    extern char read_byte();
    extern void p_read_byte();
    extern void byte_unread(char b);
    extern void byte_write(char b);
    extern void p_byte_write();
    extern bool has_jo_p();
    extern void p_has_jo_p();
    extern jo_t read_jo();
    extern void p_read_jo();
    extern void string_unread(char* str);
    extern void p_string_unread();
    extern void jo_unread(jo_t jo);
    extern void p_newline();
    extern void p_space();
    extern void expose_io();
    extern cell local_find(jo_t name);
    extern void ins_local();
    extern void set_local(jo_t name, jo_t tag, cell data);
    extern void ins_set_local();
    extern void expose_local();
    extern cell dynamic_local_find(jo_t name);
    extern void ins_dynamic_local();
    extern void set_dynamic_local(jo_t name, jo_t tag, cell data);
    extern void ins_set_dynamic_local();
    extern void expose_dynamic_local();
    extern struct stack* compiling_stack; // of jojo

    extern void p_compiling_stack_inc();
    extern void emit(cell n);
    extern void emit_jojo_end();
      // :local
      extern bool local_string_p(char* str);
      // :local!
      extern bool set_local_string_p(char* str);
      // .field
      extern bool field_string_p(char* str);
      // .field!
      extern bool set_field_string_p(char* str);
      // <tag>
      extern bool tag_string_p(char* str);
    extern void compile_jo(jo_t jo);
    extern void compile_until_meet_jo(jo_t ending_jo);
    extern jo_t compile_until_meet_jo_or_jo(jo_t ending_jo1, jo_t ending_jo2);
    extern void p_compile_until_round_ket();
    extern jo_t* compile_jojo_until_ket(jo_t ket);
    extern void expose_compiler();
    extern void k_ignore();
    extern void ins_lit();
    extern void ins_jmp();
    extern void ins_jz();
    //// if then
    //   (if a b p? then c d)
    //// ==>
    //     a b p? jz[:end-of-then]
    //     c d
    //   :end-of-then

    //// if then else
    //   (if a b p? then c d else e f)
    //// ==>
    //     a b p? jz[:end-of-then]
    //     c d jmp[:end-of-else]
    //   :end-of-then
    //     e f
    //   :end-of-else

    extern void k_if();
    extern void compile_maybe_square();
    //   (case [...]
    //     tag [...]
    //     ...)
    //// ==>
    //     [...]
    //     dup tag 'tag eq? jz[:end-of-this-case]
    //     drop [...] jmp[:end-of-case]
    //   :end-of-this-case
    //     ... ...
    //   :end-of-case
    //     drop

    extern void k_case();
    //   (cond
    //     [:t1 leaf? :t2 leaf? and] [...]
    //     [:t1 node? :t2 node? and] [...]
    //     else [else-body])
    //// ==>
    //     [:t1 leaf? :t2 leaf? and] jz[:end-of-this-cond]
    //     [...] jmp[:end-of-cond]
    //   :end-of-this-cond
    //     [:t1 node? :t2 node? and] jz[:end-of-this-cond]
    //     [...] jmp[:end-of-cond]
    //   :end-of-this-cond
    //     [else-body]
    //   :end-of-cond

    extern void k_cond();
    extern void p_recur();
    extern void expose_control();
    extern bool test_flag;
    extern void p_test_flag();
    extern void p_test_flag_on();
    extern void p_test_flag_off();
    #define MAX_FIELDS 1024

    extern void k_plus_data();
    extern void k_arrow();
    extern void k_plus_jojo();
    extern void expose_top();
    extern bool local_env_empty_p(struct local* lr);

    extern void local_env_print(struct local* lr);
    extern void data_print(jo_t tag, cell data);
    extern void p_data_print();
    extern jo_t* jojo_print_one(jo_t* jojo);
    extern void jojo_print(jo_t* jojo);
    extern void p_print_ds();
    extern void print_return_point(struct rp p);
    extern void p_print_rs();
    extern bool repl_flag;
    extern void p_repl_flag();
    extern void p_repl_flag_on();
    extern void p_repl_flag_off();
    extern void repl_one_step();
    extern void repl(struct input_stack* input_stack);
    extern cell debug_repl_level;

    extern void debug_repl(struct input_stack* input_stack);
    extern void p_debug();
      extern void kernel_signal_handler(int sig, siginfo_t *siginfo, void *ucontext);
      extern void init_kernel_signal_handler();
    extern void expose_repl();
    extern bool step_flag;
    extern cell stepper_counter;
    extern cell pending_steps;

    extern void report_one_step();
    // do not handle tail call
    extern void p_step();
    extern void expose_step();
    extern void p_true();
    extern void p_false();
    extern void p_not();
    extern void p_and();
    extern void p_or();
    extern void expose_bool();
    extern struct gp* new_string_gp(char* str);
    extern void compile_string();
    extern void p_read_line();
    extern void p_string_to_jo();
    extern void expose_string();
    extern void p_inc();
    extern void p_dec();
    extern void p_neg();
    extern void p_add();
    extern void p_sub();
    extern void p_mul();
    extern void p_div();
    extern void p_mod();
    extern void p_gt_p();
    extern void p_lt_p();
    extern void p_gteq_p();
    extern void p_lteq_p();
    extern void p_int_write();
    extern void expose_int();
    extern void p_round_bar()    ;
    extern void p_round_ket()    ;
    extern void p_square_bar()   ;
    extern void p_square_ket()   ;
    extern void p_flower_bar()   ;
    extern void p_flower_ket()   ;
    extern void p_doublequote()  ;
    extern void p_singlequote()  ;
    extern void p_backquote()    ;
    extern void p_comma()        ;
    extern void p_jo_write();
    extern void p_jo_unread();
    extern void p_jo_apply();
    extern void p_jo_to_int();
    extern void p_jo_to_byte();
    extern void p_int_jo_p();
    extern void p_local_jo_p();
    extern void p_set_local_jo_p();
    extern void p_field_jo_p();
    extern void p_set_field_jo_p();
    extern void p_tag_jo_p();
    extern bool underscore_string_p(char* str);
    extern void p_underscore_jo_p();
    extern void p_get_local_jo_to_set_local_jo();
    extern bool dynamic_local_string_p(char* str);
    extern bool set_dynamic_local_string_p(char* str);
    extern void p_dynamic_local_jo_p();
    extern void p_set_dynamic_local_jo_p();
    extern void p_jo_to_string();
    extern void p_jo_bound_p();
    extern void expose_jo();
    extern void p_compiling_stack_tos();
    extern void p_compiling_stack_drop();
    extern void p_compiling_stack_push();
    extern void p_set_offset_to_here();
    extern void p_tag_change();
    extern void p_allocate();
    extern void p_free();
    extern void p_set_cell();
    extern void p_get_cell();
    extern void p_set_byte();
    extern void p_get_byte();
    extern void expose_address();
    extern struct gp* new_array_gp(cell* array);
    extern void p_new_array();
    extern void p_array_length();
    extern void p_array_ref();
    extern void p_array_set();
    extern void p_mark();
    extern cell collect_find_length();
    extern void p_collect();
    extern void expose_array();
    extern void gc_local_env(gc_state_t gc_state, struct gp* gp);
    // caller free
    extern struct local* current_local_record();
    extern void p_current_local_env();
    extern void set_local_record(struct local* lr);
    extern void p_closure_exe();
    extern void k_closure();
    extern void expose_closure();
    extern void p_error_number_print();
    extern void path_open(int flag);
    extern void p_path_open_read();
    extern void p_path_open_write();
    extern void p_path_open_read_and_write();
    extern void p_path_open_create();
    extern void p_file_close();
    extern void p_file_read();
    extern void p_file_write();
    extern void p_file_input_stack();
    extern void erase_real_path_to_dir(char* path);

    // caller free
    extern char* current_reading_dir();
    extern void p_current_reading_dir();
    // caller free
    extern char* current_running_dir();
    extern void p_current_running_dir();
    extern void expose_file();
    extern cell cmd_number;

    extern void p_cmd_number();
    extern char** cmd_string_array;

    extern void p_index_to_cmd_string();
    extern void p_find_env_string();
    extern void expose_system();
    extern void ccall (char* function_name, void* lib);
    extern void p_path_load_clib();
    extern void expose_cffi();
    extern void p_core_flag();
    extern void p_core_flag_on();
    extern void p_core_flag_off();
    extern void load_core();
    extern void p_name_bind();
    extern void p_jo_emit();
    extern void p_emit_lit();
    extern void p_emit_zero();
    extern void p_jo_emit_local();
    extern void p_jo_emit_set_local();
    extern void p_jo_emit_dynamic_local();
    extern void p_jo_emit_set_dynamic_local();
    extern void p_jo_emit_field();
    extern void p_jo_emit_set_field();
    extern void p_emit_jz();
    extern void p_emit_jmp();
    extern void p_name_bind_data();
    extern void p_name_bind_gene();
    extern void p_name_bind_disp_to_jojo();
    extern void p_name_bind_disp_defalut_to_jojo();
    extern void p_class_to_tag();
    extern void p_cells_copy();
    extern void expose_core();
    extern void report_local_record();
    extern void expose_report();
    extern void p1();
    extern void expose_play();
    extern void init_system();
    extern void init_jotable();
    extern void init_literal_jo();
    extern jo_t jojo_area[];

    extern void init_stacks();
    extern void init_expose();
  #endif
