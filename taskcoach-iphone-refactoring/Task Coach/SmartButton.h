//
//  SmartButton.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 09/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface SmartButton : UIButton
{
    void (^callback)(id);
}

- (void)setCallback:(void (^)(id))callback;

@end
