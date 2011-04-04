//
//  SmartActionSheet.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 04/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "SmartActionSheet.h"


@implementation SmartActionSheet

- (id)initWithTitle:(NSString *)title cancelButtonTitle:(NSString *)cancelButtonTitle cancelAction:(void (^)(void))cancelAction 
{
    if ((self = [super initWithTitle:title delegate:self cancelButtonTitle:cancelButtonTitle destructiveButtonTitle:nil otherButtonTitles:nil]))
    {
        actions = [[NSMutableArray alloc] init];

        void (^action)(void);
        action = Block_copy(cancelAction);
        [actions addObject:action];
        Block_release(action);
    }

    return self;
}

- (void)dealloc
{
    [actions release];

    [super dealloc];
}

- (void)addAction:(void (^)(void))action withTitle:(NSString *)title
{
    void (^actionCopy)(void);
    actionCopy = Block_copy(action);
    [actions addObject:actionCopy];
    Block_release(actionCopy);

    [self addButtonWithTitle:title];
}

- (void)actionSheet:(UIActionSheet *)actionSheet clickedButtonAtIndex:(NSInteger)buttonIndex
{
    void (^action)(void);
    action = [actions objectAtIndex:buttonIndex];
    action();
}

@end
