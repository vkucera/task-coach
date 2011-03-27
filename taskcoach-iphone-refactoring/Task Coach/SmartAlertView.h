//
//  SmartAlertView.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 18/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface SmartAlertView : UIAlertView <UIAlertViewDelegate>
{
    NSMutableArray *actions;
}

- (id)initWithTitle:(NSString *)title message:(NSString *)message cancelButtonTitle:(NSString *)cancelButtonTitle
       cancelAction:(void (^)(void))cancelAction;

- (void)addAction:(void (^)(void))action withTitle:(NSString *)title;

@end
