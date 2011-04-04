//
//  SmartActionSheet.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 04/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface SmartActionSheet : UIActionSheet <UIActionSheetDelegate>
{
    NSMutableArray *actions;
}

- (id)initWithTitle:(NSString *)title cancelButtonTitle:(NSString *)cancelButtonTitle cancelAction:(void (^)(void))cancelAction;

- (void)addAction:(void (^)(void))action withTitle:(NSString *)title;

@end
