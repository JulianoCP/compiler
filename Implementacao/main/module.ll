; ModuleID = "module.bc"
target triple = "x86_64-pc-linux-gnu"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"

declare void @"escrevaInteiro"(i32 %".1") 

declare void @"escrevaFlutuante"(float %".1") 

declare i32 @"leiaInteiro"() 

declare float @"leiaFlutuante"() 

define i32 @"main"() 
{
entry:
  %"retorno" = alloca i32, align 4
  store i32 0, i32* %"retorno"
  %"x" = alloca i32, align 4
  %"y" = alloca float, align 4
  store i32 0, i32* %"x"
}
