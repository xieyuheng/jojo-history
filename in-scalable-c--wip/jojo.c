    #include <sys/types.h>
    #include <sys/stat.h>
    #include <unistd.h>
    #include <stdio.h>
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
    #include <assert.h>
    #include <stdlib.h>
    typedef enum { false, true } bool;
    typedef struct _env_t env_t;
    typedef
    void
    prim_fn (env_t *env);
    typedef enum {
        PRIM_INS,
        CALL_INS,
    } ins_tag_t;

    typedef struct {
        ins_tag_t tag;
        union {
            prim_fn *prim;
            char *name;
        };
    } ins_u;
    typedef enum {
        JOJO_DEN,
        DATA_DEN,
        VAR_DEN,
        MACRO_DEN,
        KEYWORD_DEN,
    } den_tag_t;

    typedef struct {
        den_tag_t tag;
        union {

        };
    } den_u;
    typedef enum {
        BOOL_OBJ,
        INT_OBJ,
    } obj_tag_t;

    typedef struct {
        obj_tag_t tag;
        union {
            bool bool_obj;
            int int_obj;
        };
    } obj_u;
    void
    ins_exe (ins_u ins, env_t *env);
    typedef struct _name_dict_t name_dict_t;
    typedef struct _data_stack_t data_stack_t;
    typedef struct _frame_stack_t frame_stack_t;
    typedef struct _macro_stack_t macro_stack_t;

    struct _env_t {
        name_dict_t *name_dict;
        data_stack_t *data_stack;
        frame_stack_t *frame_stack;
    };
    env_t *
    new_env ()
    {
        env_t *self = malloc (sizeof (env_t));
        self->name_dict = new_name_dict ();
        self->data_stack = new_data_stack ();
        self->frame_stack = new_frame_stack ();
        return self;
    }
    void
    destroy_env (env_t **self_pt)
    {
        assert (self_pt);
        if (*self_pt) {
            env_t *self = *self_pt;
            destroy_name_dict (&self->name_dict);
            destroy_data_stack (&self->data_stack);
            destroy_frame_stack (&self->frame_stack);
            free (self);
            *self_pt = NULL;
        }
    }
      struct _name_dict_t {

      };
      typedef struct _frame_t frame_t;

      struct _frame_stack_t {

      };
      struct _frame_t {
          size_t index;
          size_t length;
          ins_u *body;
      };
      frame_t *
      frame_stack_tos (frame_stack_t *frame_stack)
      {

      }
      struct _data_stack_t {

      };
      obj_u
      data_stack_pop (env_t *env)
      {

      }
      struct _macro_stack_t {

      };
    typedef
    void
    exe_fn (ins_u ins, env_t *env);
    void
    prim_exe (ins_u ins, env_t *env)
    {
        prim_fn *prim = ins.prim;
        prim (env);
    }
    void
    call_exe (ins_u ins, env_t *env)
    {

    }
    void
    jz_exe (ins_u ins, env_t *env)
    {

    }
    exe_fn *
    EXE_ARRAY[] = {
       prim_exe,
       call_exe,
    };
    void
    ins_exe (ins_u ins, env_t *env)
    {
        exe_fn *exe = EXE_ARRAY[ins.tag];
        exe (ins, env);
    }
    void
    next (env_t *env)
    {
        frame_t *frame = frame_stack_tos (env->frame_stack);
        ins_u ins = frame->body[frame->index];
        frame->index = frame->index + 1;
        ins_exe (ins, env);
    }
      void
      int_add (env_t *env)
      {
          obj_u a = data_stack_pop (env);
          obj_u b = data_stack_pop (env);
          obj_u c;
          c.tag = INT_OBJ;
          c.int_obj = a.int_obj + b.int_obj;
          data_stack_push (env, c);
      }
    int
    main (void) {
        return 0;
    }
