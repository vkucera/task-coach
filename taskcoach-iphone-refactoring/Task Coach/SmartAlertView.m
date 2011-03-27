//
//  SmartAlertView.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 18/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "SmartAlertView.h"


@implementation SmartAlertView

- (id)initWithTitle:(NSString *)title message:(NSString *)message cancelButtonTitle:(NSString *)cancelButtonTitle
       cancelAction:(void (^)(void))cancelAction
{
    if ((self = [super initWithTitle:title message:message delegate:self cancelButtonTitle:cancelButtonTitle otherButtonTitles:nil]))
    {
        actions = [[NSMutableArray alloc] init];
        // [actions addObject:[NSBlockOperation blockOperationWithBlock:cancelAction]];
        void (^action)(void) = Block_copy(cancelAction);
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
    [self addButtonWithTitle:title];
    // [actions addObject:[NSBlockOperation blockOperationWithBlock:action]];
    void (^theAction)(void) = Block_copy(action);
    [actions addObject:theAction];
    Block_release(theAction);
}

#pragma mark - Delegate

- (void)alertView:(UIAlertView *)alertView didDismissWithButtonIndex:(NSInteger)buttonIndex
{
    void (^action)(void);
    action = [actions objectAtIndex:buttonIndex];
    action();
}

@end
