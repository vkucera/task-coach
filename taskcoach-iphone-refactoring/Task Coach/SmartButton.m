//
//  SmartButton.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 09/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "SmartButton.h"


@implementation SmartButton

- (void)setCallback:(void (^)(id))theCallback
{
    if (callback)
    {
        Block_release(callback);
        [self removeTarget:self action:@selector(onClick:) forControlEvents:UIControlEventTouchUpInside];
    }
    callback = Block_copy(theCallback);
    [self addTarget:self action:@selector(onClick:) forControlEvents:UIControlEventTouchUpInside];
}

- (void)dealloc
{
    if (callback)
        Block_release(callback);
    [self removeTarget:self action:@selector(onClick:) forControlEvents:UIControlEventTouchUpInside];
    [super dealloc];
}

- (void)onClick:(UIButton *)button
{
    callback(button);
}

@end
